from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_connection, create_table

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
@app.get("/alerts")
def get_alerts():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT cpu, memory, disk, timestamp
        FROM metrics
        WHERE cpu > 50 OR memory > 70 OR disk > 80
        ORDER BY id DESC
        LIMIT 5
    """)

    rows = cursor.fetchall()
    conn.close()

    alerts = []

    for r in rows:
        cpu = r[0]
        memory = r[1]
        disk = r[2]
        time = r[3]

        if cpu > 50:
            message = f"High CPU Usage: {cpu}%"
        elif memory > 70:
            message = f"High Memory Usage: {memory}%"
        elif disk > 80:
            message = f"Disk Full: {disk}%"
        else:
            message = "System Alert"

        alerts.append({
            "message": message,
            "time": str(time)
        })

    return alerts