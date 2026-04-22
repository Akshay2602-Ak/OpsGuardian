from fastapi import FastAPI
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
    return {"message": "OpsGuardian Backend is Running 🚀"}


# 🔴 RESET DATABASE
@app.get("/reset")
def reset():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM metrics")
    cursor.execute("DELETE FROM alerts")

    conn.commit()
    conn.close()

    return {"status": "database cleared "}


# 🔴 POST METRICS
@app.post("/metrics")
def receive_metrics(data: dict):
    conn = None
    try:
        cpu = float(data.get("cpu", 0))
        memory = float(data.get("memory", 0))
        disk = float(data.get("disk", 0))

        conn = create_connection()
        cursor = conn.cursor()

        # ✅ INSERT DATA
        cursor.execute(
            "INSERT INTO metrics (cpu, memory, disk) VALUES (%s, %s, %s)",
            (cpu, memory, disk)
        )

        # 🔥 ALERT LOGIC (use separate ifs)
        alerts = []

        if cpu > 50:
            alerts.append(f"High CPU: {cpu}%")

        if memory > 70:
            alerts.append(f"High Memory: {memory}%")

        if disk > 80:
            alerts.append(f"Disk Full: {disk}%")

        # ✅ STORE + SEND ALERTS
        for msg in alerts:
            cursor.execute(
                "INSERT INTO alerts (message) VALUES (%s)",
                (msg,)
            )
            send_email_alert(msg)

        conn.commit()
        return {"status": "ok"}

    except Exception as e:
        print("❌ ERROR:", e)
        return {"error": str(e)}

    finally:
        if conn:
            conn.close()


# 🟢 GET METRICS (LATEST ONLY)
@app.get("/metrics")
def get_metrics():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, cpu, memory, disk, timestamp
        FROM metrics
        ORDER BY id DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "cpu": float(r[1]),
            "memory": float(r[2]),
            "disk": float(r[3]),
            "time": str(r[4])
        }
        for r in rows
    ]


# 🟡 GET ALERTS
@app.get("/alerts")
def get_alerts():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, message, timestamp
        FROM alerts
        ORDER BY id DESC
        LIMIT 5
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "message": r[1],
            "time": str(r[2])
        }
        for r in rows
    ]
