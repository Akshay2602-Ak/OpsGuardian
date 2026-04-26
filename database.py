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
        device_name TEXT,
        cpu REAL,
        memory REAL,
        disk REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    ALTER TABLE metrics 
    ADD COLUMN IF NOT EXISTS device_name TEXT
    """)

    conn.commit()
    conn.close()