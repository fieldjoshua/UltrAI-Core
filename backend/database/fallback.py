"""
Database fallback for the Ultra backend.

This module provides fallback functionality when the PostgreSQL database is unavailable.
It creates a wrapper around SQLAlchemy operations that fallback to in-memory database.
"""

import os
import threading
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Generator, Type, Union, Tuple

from backend.utils.logging import get_logger
from backend.utils.dependency_manager import dependency_registry, sqlalchemy_dependency
from backend.database.memory_db import memory_db, MemoryTable

# Set up logger
logger = get_logger("database_fallback", "logs/database.log")

# Check if fallback is enabled
ENABLE_DB_FALLBACK = os.getenv("ENABLE_DB_FALLBACK", "true").lower() in ("true", "1", "yes")
DB_CONNECTION_TIMEOUT = int(os.getenv("DB_CONNECTION_TIMEOUT", "5"))  # Seconds


class FallbackSession:
    """Fallback session for database operations"""

    def __init__(self, use_fallback: bool = False):
        """
        Initialize fallback session.
        
        Args:
            use_fallback: Force using fallback implementation
        """
        self.use_fallback = use_fallback
        self.committed = False
        self.flushed = False
        self.closed = False
        self.tables_map: Dict[str, MemoryTable] = {}
        self.pending_operations: List[Dict[str, Any]] = []
        self.query_class = FallbackQuery

    def add(self, instance: Any) -> None:
        """
        Add instance to session.
        
        Args:
            instance: The model instance to add
        """
        if not hasattr(instance, "__table__"):
            logger.warning(f"Cannot add instance without __table__ attribute: {instance}")
            return
            
        table_name = instance.__tablename__
        
        # Ensure we have the table
        if table_name not in self.tables_map:
            self.tables_map[table_name] = memory_db.create_table(table_name)
            
        # Get primary key value if available
        pk_name = "id"  # Default primary key name
        pk_value = getattr(instance, pk_name, None)
        
        # Add operation to pending list
        self.pending_operations.append({
            "type": "add",
            "table": table_name,
            "record": self._instance_to_dict(instance),
            "pk_value": pk_value
        })
        
    def delete(self, instance: Any) -> None:
        """
        Mark instance for deletion.
        
        Args:
            instance: The model instance to delete
        """
        if not hasattr(instance, "__table__"):
            logger.warning(f"Cannot delete instance without __table__ attribute: {instance}")
            return
            
        table_name = instance.__tablename__
        
        # Ensure we have the table
        if table_name not in self.tables_map:
            self.tables_map[table_name] = memory_db.create_table(table_name)
            
        # Get primary key value
        pk_name = "id"  # Default primary key name
        pk_value = getattr(instance, pk_name, None)
        
        if pk_value is None:
            logger.warning(f"Cannot delete instance without primary key: {instance}")
            return
            
        # Add operation to pending list
        self.pending_operations.append({
            "type": "delete",
            "table": table_name,
            "pk_value": pk_value
        })

    def flush(self) -> None:
        """Flush pending changes"""
        if self.flushed:
            return
            
        # Process pending operations
        self._process_operations()
        
        self.flushed = True

    def commit(self) -> None:
        """Commit changes"""
        if self.committed:
            return
            
        # Flush if not already done
        if not self.flushed:
            self.flush()
            
        # When using memory DB, commit is basically flush
        # We would add transaction support here for real DB
        
        self.committed = True

    def rollback(self) -> None:
        """Rollback changes"""
        # Just clear pending operations
        self.pending_operations = []
        self.flushed = False
        self.committed = False

    def close(self) -> None:
        """Close the session"""
        # Nothing to do for memory DB
        self.closed = True

    def query(self, *entities: Any) -> 'FallbackQuery':
        """
        Create a query object.
        
        Args:
            entities: Entities to query
            
        Returns:
            Query object
        """
        # Create a query with the main entity type
        if not entities:
            logger.warning("Empty query entities")
            return self.query_class(None, self)
            
        main_entity = entities[0]
        return self.query_class(main_entity, self)

    def _process_operations(self) -> None:
        """Process pending operations"""
        for operation in self.pending_operations:
            op_type = operation.get("type")
            table_name = operation.get("table")
            
            if not memory_db.table_exists(table_name):
                memory_db.create_table(table_name)
                
            table = memory_db.get_table(table_name)
            
            if op_type == "add":
                record = operation.get("record", {})
                pk_value = operation.get("pk_value")
                
                if pk_value is not None:
                    # Check if record exists
                    existing = table.query({"id": pk_value})
                    if existing:
                        # Update existing record
                        table.update(str(pk_value), record)
                    else:
                        # Insert new record
                        table.insert(record, str(pk_value))
                else:
                    # Insert new record
                    table.insert(record)
                    
            elif op_type == "delete":
                pk_value = operation.get("pk_value")
                if pk_value is not None:
                    table.delete(str(pk_value))
        
        # Clear pending operations
        self.pending_operations = []

    def _instance_to_dict(self, instance: Any) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        
        Args:
            instance: Model instance
            
        Returns:
            Dictionary representation
        """
        result = {}
        
        # Get all attributes that don't start with _
        for attr_name in dir(instance):
            if attr_name.startswith("_"):
                continue
                
            attr_value = getattr(instance, attr_name)
            
            # Skip methods and other non-data attributes
            if callable(attr_value):
                continue
                
            # Skip relationship attributes
            if hasattr(attr_value, "__table__"):
                continue
                
            # Add attribute to result
            result[attr_name] = attr_value
            
        return result


class FallbackQuery:
    """Fallback query implementation"""

    def __init__(self, entity: Any, session: FallbackSession):
        """
        Initialize fallback query.
        
        Args:
            entity: Entity to query
            session: Fallback session
        """
        self.entity = entity
        self.session = session
        self.filters = []
        self.order_by_clauses = []
        self._limit = None
        self._offset = None
        self._all_entities = [entity] if entity else []

    def filter(self, *criteria: Any) -> 'FallbackQuery':
        """
        Add filtering criteria.
        
        Args:
            criteria: Filter criteria
            
        Returns:
            Query object
        """
        # Process criteria and add to filters
        # In real implementation, we would parse SQLAlchemy criteria
        # For now, just store them
        self.filters.extend(criteria)
        return self

    def filter_by(self, **kwargs: Any) -> 'FallbackQuery':
        """
        Add filtering by keyword arguments.
        
        Args:
            kwargs: Filter criteria
            
        Returns:
            Query object
        """
        self.filters.append(kwargs)
        return self

    def order_by(self, *clauses: Any) -> 'FallbackQuery':
        """
        Add ordering clauses.
        
        Args:
            clauses: Order by clauses
            
        Returns:
            Query object
        """
        self.order_by_clauses.extend(clauses)
        return self

    def limit(self, limit: int) -> 'FallbackQuery':
        """
        Set limit.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            Query object
        """
        self._limit = limit
        return self

    def offset(self, offset: int) -> 'FallbackQuery':
        """
        Set offset.
        
        Args:
            offset: Offset for results
            
        Returns:
            Query object
        """
        self._offset = offset
        return self

    def all(self) -> List[Any]:
        """
        Get all results.
        
        Returns:
            List of results
        """
        if not self.entity or not hasattr(self.entity, "__tablename__"):
            return []
            
        # Get table
        table_name = self.entity.__tablename__
        if not memory_db.table_exists(table_name):
            return []
            
        table = memory_db.get_table(table_name)
        
        # Convert filters to conditions
        conditions = self._convert_filters_to_conditions()
        
        # Execute query
        records = table.query(conditions)
        
        # Apply ordering (not implemented yet)
        
        # Apply offset and limit
        if self._offset is not None:
            records = records[self._offset:]
            
        if self._limit is not None:
            records = records[:self._limit]
            
        # Convert records to instances
        return [self._dict_to_instance(record) for record in records]

    def first(self) -> Optional[Any]:
        """
        Get first result.
        
        Returns:
            First result or None
        """
        results = self.limit(1).all()
        return results[0] if results else None

    def one(self) -> Any:
        """
        Get exactly one result.
        
        Returns:
            Result
            
        Raises:
            Exception: If not exactly one result
        """
        results = self.limit(2).all()
        
        if not results:
            raise Exception("No results found")
            
        if len(results) > 1:
            raise Exception("Multiple results found")
            
        return results[0]

    def one_or_none(self) -> Optional[Any]:
        """
        Get one result or None.
        
        Returns:
            Result or None
            
        Raises:
            Exception: If multiple results
        """
        results = self.limit(2).all()
        
        if not results:
            return None
            
        if len(results) > 1:
            raise Exception("Multiple results found")
            
        return results[0]

    def count(self) -> int:
        """
        Get count of results.
        
        Returns:
            Count of results
        """
        # Just get all results and count them
        # Not efficient, but works for fallback
        return len(self.all())

    def _convert_filters_to_conditions(self) -> Dict[str, Any]:
        """
        Convert filters to conditions.
        
        Returns:
            Conditions dictionary
        """
        conditions = {}
        
        for filter_item in self.filters:
            if isinstance(filter_item, dict):
                # Direct dictionary of conditions
                conditions.update(filter_item)
            else:
                # Skip unsupported filters
                # In real implementation, we would parse SQLAlchemy criteria
                continue
                
        return conditions

    def _dict_to_instance(self, record: Dict[str, Any]) -> Any:
        """
        Convert dictionary to model instance.
        
        Args:
            record: Record dictionary
            
        Returns:
            Model instance
        """
        if not self.entity:
            return record
            
        # Create instance
        instance = self.entity()
        
        # Set attributes
        for key, value in record.items():
            setattr(instance, key, value)
            
        return instance


@contextmanager
def fallback_session() -> Generator[FallbackSession, None, None]:
    """
    Context manager for fallback session.
    
    Yields:
        Fallback session
    """
    session = FallbackSession()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


# Create an alias for compatibility
get_fallback_db = fallback_session