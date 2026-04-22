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
    return {"message": "OpsGuardian Backend is Running 🚀"}


# 🔴 POST METRICS
@app.post("/metrics")
def receive_metrics(data: dict):
    conn = None
    try:
        cpu = data.get("cpu", 0)
        memory = data.get("memory", 0)
        disk = data.get("disk", 0)

        conn = create_connection()
        cursor = conn.cursor()

        # ✅ CLEAN OLD DATA (metrics)
        cursor.execute("""
            DELETE FROM metrics
            WHERE timestamp < NOW() - INTERVAL '30 seconds'
        """)

        # ✅ CLEAN OLD ALERTS (important)
        cursor.execute("""
            DELETE FROM alerts
            WHERE timestamp < NOW() - INTERVAL '1 minute'
        """)

        # ✅ INSERT NEW METRICS
        cursor.execute(
            "INSERT INTO metrics (cpu, memory, disk) VALUES (%s, %s, %s)",
            (cpu, memory, disk)
        )

        # 🔥 ALERT LOGIC
        msg = None
        if cpu > 50:
            msg = f"High CPU: {cpu}%"
        elif memory > 70:
            msg = f"High Memory: {memory}%"
        elif disk > 80:
            msg = f"Disk Full: {disk}%"

        if msg:
            cursor.execute(
                "INSERT INTO alerts (message) VALUES (%s)",
                (msg,)
            )

        conn.commit()
        return {"status": "ok"}

    except Exception as e:
        print("❌ ERROR:", e)
        return {"error": str(e)}

    finally:
        if conn:
            conn.close()


# 🟢 GET METRICS (ONLY FRESH DATA)
@app.get("/metrics")
def get_metrics():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, cpu, memory, disk, timestamp
        FROM metrics
        WHERE timestamp > NOW() - INTERVAL '30 seconds'
        ORDER BY id DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "cpu": r[1],
            "memory": r[2],
            "disk": r[3],
            "time": str(r[4])
        }
        for r in rows
    ]


# 🟡 GET ALERTS (ONLY RECENT)
@app.get("/alerts")
def get_alerts():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, message, timestamp
        FROM alerts
        WHERE timestamp > NOW() - INTERVAL '1 minute'
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