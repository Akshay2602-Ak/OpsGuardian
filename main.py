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
    device_name = data.get("device_name", "Unknown Device")
    cpu = float(data.get("cpu", 0))
    memory = float(data.get("memory", 0))
    disk = float(data.get("disk", 0))

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO metrics (device_name, cpu, memory, disk) VALUES (%s, %s, %s, %s)",
        (device_name, cpu, memory, disk)
    )

    alerts = []

    if cpu > 50:
        alerts.append(f"{device_name} - High CPU Usage: {cpu}%")

    if memory > 70:
        alerts.append(f"{device_name} - High Memory Usage: {memory}%")

    if disk > 80:
        alerts.append(f"{device_name} - Disk Full: {disk}%")

    conn.commit()
    conn.close()

    for alert in alerts:
        background_tasks.add_task(send_email_alert, alert)

    return {"status": "stored", "device": device_name, "alerts": alerts}


@app.get("/metrics")
def get_metrics(device: str = None):
    conn = create_connection()
    cursor = conn.cursor()

    if device and device != "All":
        cursor.execute("""
            SELECT device_name, cpu, memory, disk, timestamp
            FROM metrics
            WHERE device_name = %s
            ORDER BY id DESC
            LIMIT 10
        """, (device,))
    else:
        cursor.execute("""
            SELECT device_name, cpu, memory, disk, timestamp
            FROM metrics
            ORDER BY id DESC
            LIMIT 10
        """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "device_name": r[0],
            "cpu": float(r[1]),
            "memory": float(r[2]),
            "disk": float(r[3]),
            "time": str(r[4])
        }
        for r in rows
    ]

@app.get("/alerts")
def get_alerts():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT device_name, cpu, memory, disk, timestamp
        FROM metrics
        WHERE cpu > 50 OR memory > 70 OR disk > 80
        ORDER BY id DESC
        LIMIT 5
    """)

    rows = cursor.fetchall()
    conn.close()

    alerts = []

    for r in rows:
        device_name = r[0] or "Unknown Device"
        cpu = float(r[1])
        memory = float(r[2])
        disk = float(r[3])
        time = r[4]

        if cpu > 50:
            message = f"{device_name} - High CPU Usage: {cpu}%"
        elif memory > 70:
            message = f"{device_name} - High Memory Usage: {memory}%"
        elif disk > 80:
            message = f"{device_name} - Disk Full: {disk}%"
        else:
            message = f"{device_name} - System Alert"

        alerts.append({
            "device_name": device_name,
            "message": message,
            "time": str(time)
        })

    return alerts
@app.get("/devices")
def get_devices():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT device_name FROM metrics
    """)

    rows = cursor.fetchall()
    conn.close()

    devices = [r[0] for r in rows if r[0]]

    return devices
# @app.get("/test-email")
# def test_email(background_tasks: BackgroundTasks):
#     background_tasks.add_task(send_email_alert, "Test Email from OpsGuardian")
#     return {"status": "test email triggered"}