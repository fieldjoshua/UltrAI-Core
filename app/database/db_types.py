"""
Database type utilities for cross-database compatibility.

This module provides database-agnostic type definitions that work
with both PostgreSQL and SQLite.
"""

import json
from sqlalchemy import String, Text, TypeDecorator
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY, JSONB as PG_JSONB


class JSONEncodedDict(TypeDecorator):
    """Store a dict as JSON text for SQLite compatibility."""
    
    impl = Text
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class StringList(TypeDecorator):
    """Store a list of strings as JSON text for SQLite compatibility."""
    
    impl = Text
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


def get_json_type(dialect_name=None):
    """Get appropriate JSON type for the database dialect."""
    if dialect_name == "postgresql":
        return PG_JSONB
    return JSONEncodedDict


def get_array_type(item_type, dialect_name=None):
    """Get appropriate array type for the database dialect."""
    if dialect_name == "postgresql":
        return PG_ARRAY(item_type)
    # For SQLite and others, use JSON-encoded list
    if item_type == String:
        return StringList
    # For other types, would need specific implementations
    return StringList