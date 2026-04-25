import os
import psycopg2
import sqlite3

DATABASE_URL = os.getenv("DATABASE_URL")


def create_connection():
    if DATABASE_URL:
        # 🌐 Railway (Postgres)
        return psycopg2.connect(DATABASE_URL)
    else:
        # 💻 Local (SQLite fallback)
        return sqlite3.connect("local.db")


def create_table():
    conn = create_connection()
    cursor = conn.cursor()

    # ✅ Detect DB type
    is_postgres = DATABASE_URL is not None

    if is_postgres:
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
    else:
        # 🔥 SQLite version
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpu REAL,
            memory REAL,
            disk REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

    conn.commit()
    conn.close()