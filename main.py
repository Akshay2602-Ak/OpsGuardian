from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from database import create_connection, create_table
from email_alert import send_email_alert

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
def receive_metrics(data: dict, background_tasks: BackgroundTasks):
    cpu = float(data.get("cpu", 0))
    memory = float(data.get("memory", 0))
    disk = float(data.get("disk", 0))

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO metrics (cpu, memory, disk) VALUES (%s, %s, %s)",
        (cpu, memory, disk)
    )

    alerts = []

    if cpu > 50:
        alerts.append(f"High CPU Usage: {cpu}%")

    if memory > 70:
        alerts.append(f"High Memory Usage: {memory}%")

    if disk > 80:
        alerts.append(f"Disk Full: {disk}%")

    conn.commit()
    conn.close()

    for alert in alerts:
        background_tasks.add_task(send_email_alert, alert)

    return {"status": "stored", "alerts": alerts}


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
            "cpu": float(r[0]),
            "memory": float(r[1]),
            "disk": float(r[2]),
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
        cpu = float(r[0])
        memory = float(r[1])
        disk = float(r[2])
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