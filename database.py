import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

def create_connection():
    return psycopg2.connect(DATABASE_URL)


def create_table():
    conn = create_connection()
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
    conn.close()