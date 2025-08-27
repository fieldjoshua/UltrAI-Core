"""
Database query optimization service.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy import text, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import QueuePool, NullPool
import time

from app.database.connection import get_db
from app.utils.logging import get_logger

logger = get_logger("db_optimization")


class DatabaseOptimizationService:
    """Service for database performance optimization."""
    
    def __init__(self):
        self.slow_query_threshold = 1.0  # seconds
        self.query_stats: Dict[str, Dict[str, Any]] = {}
    
    def setup_query_monitoring(self, engine: Engine):
        """Setup query monitoring and logging."""
        
        @event.listens_for(engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault("query_start_time", []).append(time.time())
            logger.debug(f"Query: {statement[:100]}...")
        
        @event.listens_for(engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total = time.time() - conn.info["query_start_time"].pop(-1)
            
            # Log slow queries
            if total > self.slow_query_threshold:
                logger.warning(
                    f"Slow query detected ({total:.2f}s): {statement[:200]}...",
                    extra={"duration": total, "query": statement[:500]}
                )
            
            # Track query statistics
            query_key = statement[:100]
            if query_key not in self.query_stats:
                self.query_stats[query_key] = {
                    "count": 0,
                    "total_time": 0,
                    "max_time": 0,
                    "min_time": float('inf')
                }
            
            stats = self.query_stats[query_key]
            stats["count"] += 1
            stats["total_time"] += total
            stats["max_time"] = max(stats["max_time"], total)
            stats["min_time"] = min(stats["min_time"], total)
    
    def get_query_stats(self) -> List[Dict[str, Any]]:
        """Get query performance statistics."""
        results = []
        
        for query, stats in self.query_stats.items():
            avg_time = stats["total_time"] / stats["count"] if stats["count"] > 0 else 0
            results.append({
                "query": query,
                "count": stats["count"],
                "avg_time": round(avg_time, 3),
                "total_time": round(stats["total_time"], 3),
                "max_time": round(stats["max_time"], 3),
                "min_time": round(stats["min_time"], 3) if stats["min_time"] != float('inf') else 0
            })
        
        # Sort by total time descending
        results.sort(key=lambda x: x["total_time"], reverse=True)
        
        return results
    
    async def create_indexes(self, db: Session):
        """Create performance indexes if they don't exist."""
        
        indexes = [
            # User lookups
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);",
            
            # Transaction queries
            "CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at DESC);",
            "CREATE INDEX IF NOT EXISTS idx_transactions_user_created ON transactions(user_id, created_at DESC);",
            
            # Usage tracking
            "CREATE INDEX IF NOT EXISTS idx_usage_records_user_id ON usage_records(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_usage_records_created_at ON usage_records(created_at DESC);",
            
            # Document queries  
            "CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at DESC);",
            
            # Analysis history
            "CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at DESC);",
        ]
        
        for index_sql in indexes:
            try:
                db.execute(text(index_sql))
                db.commit()
                logger.info(f"Created index: {index_sql[:50]}...")
            except Exception as e:
                logger.warning(f"Failed to create index: {e}")
                db.rollback()
    
    async def vacuum_database(self, db: Session):
        """Run VACUUM to reclaim space and update statistics."""
        try:
            # For PostgreSQL
            db.execute(text("VACUUM ANALYZE;"))
            logger.info("Database VACUUM completed")
        except Exception as e:
            logger.error(f"Failed to VACUUM database: {e}")
    
    def optimize_connection_pool(self, engine: Engine):
        """Optimize database connection pool settings."""
        
        # Get current pool class
        pool_class = engine.pool.__class__.__name__
        
        if pool_class == "QueuePool":
            # Optimize QueuePool settings
            engine.pool._recycle = 3600  # Recycle connections after 1 hour
            engine.pool._pre_ping = True  # Enable connection health checks
            logger.info("Optimized QueuePool settings")
        
        elif pool_class == "NullPool":
            logger.info("Using NullPool (no connection pooling)")
    
    def get_connection_stats(self, engine: Engine) -> Dict[str, Any]:
        """Get database connection pool statistics."""
        
        pool = engine.pool
        pool_class = pool.__class__.__name__
        
        stats = {
            "pool_class": pool_class,
            "size": getattr(pool, "size", lambda: 0)() if hasattr(pool, "size") else 0,
            "checked_in": getattr(pool, "checkedin", lambda: 0)() if hasattr(pool, "checkedin") else 0,
            "checked_out": getattr(pool, "checkedout", lambda: 0)() if hasattr(pool, "checkedout") else 0,
            "overflow": getattr(pool, "overflow", lambda: 0)() if hasattr(pool, "overflow") else 0,
            "total": getattr(pool, "total", lambda: 0)() if hasattr(pool, "total") else 0,
        }
        
        return stats


# Global instance
_db_optimization_service: Optional[DatabaseOptimizationService] = None


def get_db_optimization_service() -> DatabaseOptimizationService:
    """Get or create database optimization service."""
    global _db_optimization_service
    if _db_optimization_service is None:
        _db_optimization_service = DatabaseOptimizationService()
    return _db_optimization_service