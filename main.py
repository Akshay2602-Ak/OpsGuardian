from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_connection, create_table, create_alerts_table

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Initialize DB
create_table()
create_alerts_table()


@app.get("/")
def home():
    return {"message": "OpsGuardian Backend is Running 🚀"}


# 🔴 POST METRICS (🔥 OPTIMIZED)
@app.post("/metrics")
def receive_metrics(data: dict):
    try:
        cpu = data.get("cpu")
        memory = data.get("memory")
        disk = data.get("disk")

        print("📊 Received:", data)

        conn = create_connection()
        cursor = conn.cursor()

        # ✅ Store metrics (single write)
        cursor.execute(
            "INSERT INTO metrics (cpu, memory, disk) VALUES (?, ?, ?)",
            (cpu, memory, disk)
        )

        # 🔥 ONLY ONE ALERT (reduces DB load)
        msg = None

        if cpu > 50:
            msg = f"High CPU Usage: {cpu}%"
        elif memory > 70:
            msg = f"High Memory Usage: {memory}%"
        elif disk > 80:
            msg = f"Disk Almost Full: {disk}%"

        if msg:
            print("⚠️", msg)
            cursor.execute(
                "INSERT INTO alerts (message) VALUES (?)",
                (msg,)
            )

        conn.commit()
        conn.close()

        return {"status": "stored"}

    except Exception as e:
        print("❌ Backend Error:", e)
        return {"error": str(e)}


# 🟢 GET METRICS
@app.get("/metrics")
def get_metrics():
    try:
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

        data = []

        for row in rows:
            raw_time = row[4]
            formatted_time = raw_time.replace(" ", "T") if raw_time else None

            data.append({
                "id": row[0],
                "cpu": row[1],
                "memory": row[2],
                "disk": row[3],
                "time": formatted_time
            })

        return data

    except Exception as e:
        print("❌ Metrics Error:", e)
        return []


# 🟡 GET ALERTS
@app.get("/alerts")
def get_alerts():
    try:
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

        data = []

        for row in rows:
            raw_time = row[2]
            formatted_time = raw_time.replace(" ", "T") if raw_time else None

            data.append({
                "id": row[0],
                "message": row[1],
                "time": formatted_time
            })

        return data

    except Exception as e:
        print("❌ Alerts Error:", e)
        return []