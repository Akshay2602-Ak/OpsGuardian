from fastapi import FastAPI
from database import create_connection, create_table

app = FastAPI()

create_table()

@app.get("/")
def home():
    return {"status": "running"}

@app.post("/metrics")
def receive_metrics(data: dict):
    cpu = data.get("cpu", 0)
    memory = data.get("memory", 0)
    disk = data.get("disk", 0)

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO metrics (cpu, memory, disk) VALUES (%s, %s, %s)",
        (cpu, memory, disk)
    )

    conn.commit()
    conn.close()

    return {"status": "stored"}

@app.get("/metrics")
def get_metrics():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT cpu, memory, disk, timestamp
        FROM metrics
        ORDER BY id DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "cpu": r[0],
            "memory": r[1],
            "disk": r[2],
            "time": str(r[3])
        }
        for r in rows
    ]