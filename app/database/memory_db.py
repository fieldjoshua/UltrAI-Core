"""
In-memory database module for the Ultra backend.

This module provides a simple in-memory database implementation for the Ultra backend
when PostgreSQL is not available. It supports basic CRUD operations on a per-table basis
and maintains relationships between tables.
"""

import json
import logging
import threading
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from app.utils.logging import get_logger

# Set up logger
logger = get_logger("memory_db", "logs/memory_db.log")


class MemoryTable:
    """A simple in-memory table implementation"""

    def __init__(self, name: str):
        """
        Initialize memory table

        Args:
            name: Table name
        """
        self.name = name
        self.records: Dict[str, Dict[str, Any]] = {}
        self.indexes: Dict[str, Dict[Any, Set[str]]] = {}
        self.auto_id = 1
        self.lock = threading.RLock()  # For thread safety

    def create_index(self, column: str) -> None:
        """
        Create an index on a column

        Args:
            column: Column name to index
        """
        with self.lock:
            if column not in self.indexes:
                self.indexes[column] = {}
                # Build index for existing records
                for record_id, record in self.records.items():
                    value = record.get(column)
                    if value is not None:
                        if value not in self.indexes[column]:
                            self.indexes[column][value] = set()
                        self.indexes[column][value].add(record_id)

    def _add_to_indexes(self, record_id: str, record: Dict[str, Any]) -> None:
        """
        Add record to indexes

        Args:
            record_id: Record ID
            record: Record data
        """
        for column, index in self.indexes.items():
            value = record.get(column)
            if value is not None:
                if value not in index:
                    index[value] = set()
                index[value].add(record_id)

    def _remove_from_indexes(self, record_id: str, record: Dict[str, Any]) -> None:
        """
        Remove record from indexes

        Args:
            record_id: Record ID
            record: Record data
        """
        for column, index in self.indexes.items():
            value = record.get(column)
            if value is not None and value in index:
                index[value].discard(record_id)
                # Clean up empty sets
                if not index[value]:
                    del index[value]

    def insert(self, record: Dict[str, Any], record_id: Optional[str] = None) -> str:
        """
        Insert a record into the table

        Args:
            record: Record data
            record_id: Optional record ID (generated if not provided)

        Returns:
            Record ID
        """
        with self.lock:
            # Generate ID if not provided
            if record_id is None:
                if "id" in record and record["id"] is not None:
                    record_id = str(record["id"])
                else:
                    record_id = str(uuid.uuid4())
                    record["id"] = record_id

            # Add created_at if not present
            if "created_at" not in record:
                record["created_at"] = datetime.now().isoformat()

            # Add updated_at
            record["updated_at"] = datetime.now().isoformat()

            # Store record
            self.records[record_id] = record.copy()

            # Update indexes
            self._add_to_indexes(record_id, record)

            return record_id

    def get(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a record by ID

        Args:
            record_id: Record ID

        Returns:
            Record data or None if not found
        """
        with self.lock:
            record = self.records.get(record_id)
            return record.copy() if record else None

    def update(self, record_id: str, record: Dict[str, Any]) -> bool:
        """
        Update a record

        Args:
            record_id: Record ID
            record: New record data

        Returns:
            True if updated, False if record not found
        """
        with self.lock:
            if record_id not in self.records:
                return False

            # Get existing record
            existing = self.records[record_id]

            # Remove from indexes
            self._remove_from_indexes(record_id, existing)

            # Update record
            updated = existing.copy()
            updated.update(record)
            updated["updated_at"] = datetime.now().isoformat()

            # Store updated record
            self.records[record_id] = updated

            # Add to indexes
            self._add_to_indexes(record_id, updated)

            return True

    def delete(self, record_id: str) -> bool:
        """
        Delete a record

        Args:
            record_id: Record ID

        Returns:
            True if deleted, False if record not found
        """
        with self.lock:
            if record_id not in self.records:
                return False

            # Get existing record
            existing = self.records[record_id]

            # Remove from indexes
            self._remove_from_indexes(record_id, existing)

            # Delete record
            del self.records[record_id]

            return True

    def query(self, conditions: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Query records by conditions

        Args:
            conditions: Column-value conditions (e.g., {"name": "John"})

        Returns:
            List of matching records
        """
        with self.lock:
            if not conditions:
                # Return all records
                return [record.copy() for record in self.records.values()]

            # Find matching records using indexes where possible
            candidate_ids: Optional[Set[str]] = None

            # First pass: use indexes to narrow down candidates
            for column, value in conditions.items():
                if column in self.indexes and value in self.indexes[column]:
                    # Get IDs from index
                    index_ids = self.indexes[column][value]

                    if candidate_ids is None:
                        # First condition, set initial candidates
                        candidate_ids = index_ids.copy()
                    else:
                        # Subsequent condition, intersect with current candidates
                        candidate_ids &= index_ids

                    # Optimization: if no candidates left, return early
                    if not candidate_ids:
                        return []

            # Second pass: filter by all conditions
            results = []

            if candidate_ids is not None:
                # We have candidate IDs from indexes
                for record_id in candidate_ids:
                    record = self.records[record_id]
                    if self._matches_conditions(record, conditions):
                        results.append(record.copy())
            else:
                # No useful indexes, scan all records
                for record in self.records.values():
                    if self._matches_conditions(record, conditions):
                        results.append(record.copy())

            return results

    def _matches_conditions(
        self, record: Dict[str, Any], conditions: Dict[str, Any]
    ) -> bool:
        """
        Check if a record matches conditions

        Args:
            record: Record to check
            conditions: Conditions to match

        Returns:
            True if record matches all conditions
        """
        for column, value in conditions.items():
            if column not in record or record[column] != value:
                return False
        return True


class MemoryDB:
    """Simple in-memory database implementation"""

    def __init__(self):
        """Initialize memory database"""
        self.tables: Dict[str, MemoryTable] = {}
        self.lock = threading.RLock()  # For thread safety
        logger.info("Initialized in-memory database")

    def create_table(self, name: str) -> MemoryTable:
        """
        Create a new table

        Args:
            name: Table name

        Returns:
            Memory table instance
        """
        with self.lock:
            if name not in self.tables:
                self.tables[name] = MemoryTable(name)
                logger.info(f"Created in-memory table: {name}")
            return self.tables[name]

    def get_table(self, name: str) -> Optional[MemoryTable]:
        """
        Get a table by name

        Args:
            name: Table name

        Returns:
            Memory table instance or None if not found
        """
        return self.tables.get(name)

    def table_exists(self, name: str) -> bool:
        """
        Check if a table exists

        Args:
            name: Table name

        Returns:
            True if table exists, False otherwise
        """
        return name in self.tables

    def drop_table(self, name: str) -> bool:
        """
        Drop a table

        Args:
            name: Table name

        Returns:
            True if dropped, False if table not found
        """
        with self.lock:
            if name in self.tables:
                del self.tables[name]
                logger.info(f"Dropped in-memory table: {name}")
                return True
            return False

    def get_tables(self) -> List[str]:
        """
        Get names of all tables

        Returns:
            List of table names
        """
        return list(self.tables.keys())

    def clear(self) -> None:
        """Clear all tables and data"""
        with self.lock:
            self.tables.clear()
            logger.info("Cleared all in-memory database tables")

    def get_status(self) -> Dict[str, Any]:
        """
        Get database status

        Returns:
            Dictionary with status information
        """
        with self.lock:
            table_stats = {}
            total_records = 0

            for name, table in self.tables.items():
                record_count = len(table.records)
                table_stats[name] = {
                    "records": record_count,
                    "indexes": list(table.indexes.keys()),
                }
                total_records += record_count

            return {
                "tables_count": len(self.tables),
                "total_records": total_records,
                "tables": table_stats,
            }

    def export_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Export all data as a dictionary

        Returns:
            Dictionary with table data
        """
        with self.lock:
            result = {}

            for name, table in self.tables.items():
                result[name] = [record.copy() for record in table.records.values()]

            return result

    def import_data(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        """
        Import data into the database

        Args:
            data: Data to import
        """
        with self.lock:
            for table_name, records in data.items():
                table = self.create_table(table_name)

                for record in records:
                    # If record has an ID, use it
                    record_id = str(record.get("id")) if "id" in record else None
                    table.insert(record, record_id)

            logger.info(f"Imported data into {len(data)} tables")


# Create a global instance
memory_db = MemoryDB()
