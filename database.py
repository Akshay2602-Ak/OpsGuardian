import os
import psycopg2
from psycopg2 import pool

DATABASE_URL = os.getenv("DATABASE_URL")

# Global connection pool — initialised by init_pool() at app startup.
_pool: pool.SimpleConnectionPool | None = None


def init_pool(minconn: int = 2, maxconn: int = 10) -> None:
    """Create the global SimpleConnectionPool.  Call once at startup."""
    global _pool
    _pool = pool.SimpleConnectionPool(minconn, maxconn, DATABASE_URL)
    print(f"✅ Connection pool initialised (min={minconn}, max={maxconn})")


def get_connection() -> psycopg2.extensions.connection:
    """Borrow a connection from the pool."""
    if _pool is None:
        raise RuntimeError("Connection pool has not been initialised. Call init_pool() first.")
    return _pool.getconn()


def release_connection(conn: psycopg2.extensions.connection) -> None:
    """Return a connection to the pool so it can be reused."""
    if _pool is not None and conn is not None:
        _pool.putconn(conn)


def create_table() -> None:
    """Create the metrics and alerts tables if they don't already exist."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id SERIAL PRIMARY KEY,
            cpu REAL,
            memory REAL,
            disk REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id SERIAL PRIMARY KEY,
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
    finally:
        release_connection(conn)