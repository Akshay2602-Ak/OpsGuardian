from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_connection, create_table, create_alerts_table
from email_alert import send_email_alert

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Create tables
create_table()
create_alerts_table()


@app.get("/")
def home():
    return {"message": "OpsGuardian Backend is Running 🚀"}


# 🔴 POST METRICS
@app.post("/metrics")
def receive_metrics(data: dict):
    cpu = data.get("cpu")
    memory = data.get("memory")
    disk = data.get("disk")

    print("📊 Received:", data)

    conn = create_connection()
    cursor = conn.cursor()

    # ✅ Store metrics
    cursor.execute(
        "INSERT INTO metrics (cpu, memory, disk) VALUES (?, ?, ?)",
        (cpu, memory, disk)
    )

    # 🔥 ALERT LOGIC
    if cpu > 50:
        msg = f"High CPU Usage: {cpu}%"
        print("🚀 Sending Email...")
        send_email_alert(msg)
        cursor.execute("INSERT INTO alerts (message) VALUES (?)", (msg,))

    if memory > 70:
        msg = f"High Memory Usage: {memory}%"
        print("🚀 Sending Email...")
        send_email_alert(msg)
        cursor.execute("INSERT INTO alerts (message) VALUES (?)", (msg,))

    if disk > 80:
        msg = f"Disk Almost Full: {disk}%"
        print("🚀 Sending Email...")
        send_email_alert(msg)
        cursor.execute("INSERT INTO alerts (message) VALUES (?)", (msg,))

    conn.commit()
    conn.close()

    return {"status": "stored"}


# 🟢 GET METRICS (🔥 FIXED TIME FORMAT)
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

    data = []

    for row in rows:
        raw_time = row[4]

        # 🔥 FIX: Convert to ISO format
        formatted_time = raw_time.replace(" ", "T") if raw_time else None

        data.append({
            "id": row[0],
            "cpu": row[1],
            "memory": row[2],
            "disk": row[3],
            "time": formatted_time
        })

    return data


# 🟡 GET ALERTS (🔥 FIXED TIME FORMAT)
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