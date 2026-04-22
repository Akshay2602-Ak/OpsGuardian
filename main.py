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


@app.post("/metrics")
def receive_metrics(data: dict):
    try:
        cpu = data.get("cpu")
        memory = data.get("memory")
        disk = data.get("disk")

        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       DELETE FROM metrics
                       WHERE timestamp < NOW() - INTERVAL '5 minutes'
                       """)
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
        conn.close()

        return {"status": "ok"}

    except Exception as e:
        print("❌ ERROR:", e)
        return {"error": str(e)}


@app.get("/metrics")
def get_metrics():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, cpu, memory, disk, timestamp
        FROM metrics
        WHERE timestamp > NOW() - INTERVAL '2 minutes'
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