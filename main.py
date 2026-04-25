import threading
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_pool, get_connection, release_connection, create_table
from email_alert import send_email_alert

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Startup: initialise the connection pool, then create tables.
# ---------------------------------------------------------------------------
init_pool(minconn=2, maxconn=10)
create_table()

# ---------------------------------------------------------------------------
# Simple in-process cache (TTL = 2 seconds).
# Each entry: {"data": <result>, "ts": <epoch float>}
# ---------------------------------------------------------------------------
_CACHE_TTL = 2.0  # seconds
_cache: dict = {}
_cache_lock = threading.Lock()


def _cache_get(key: str):
    with _cache_lock:
        entry = _cache.get(key)
        if entry and (time.monotonic() - entry["ts"]) < _CACHE_TTL:
            return entry["data"]
    return None


def _cache_set(key: str, data) -> None:
    with _cache_lock:
        _cache[key] = {"data": data, "ts": time.monotonic()}


def _cache_invalidate(key: str) -> None:
    with _cache_lock:
        _cache.pop(key, None)


# ---------------------------------------------------------------------------
# Helper: fire-and-forget email in a background thread so it never blocks.
# ---------------------------------------------------------------------------
def _send_email_async(message: str) -> None:
    t = threading.Thread(target=send_email_alert, args=(message,), daemon=True)
    t.start()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def home():
    return {"message": "OpsGuardian Backend is Running 🚀"}


# 🔴 RESET DATABASE
@app.get("/reset")
def reset():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM metrics")
        cursor.execute("DELETE FROM alerts")

        conn.commit()

        # Invalidate caches so stale data isn't served after a reset.
        _cache_invalidate("metrics")
        _cache_invalidate("alerts")

        return {"status": "database cleared "}
    finally:
        release_connection(conn)


# 🔴 POST METRICS
@app.post("/metrics")
def receive_metrics(data: dict):
    conn = None
    try:
        cpu = float(data.get("cpu", 0))
        memory = float(data.get("memory", 0))
        disk = float(data.get("disk", 0))

        conn = get_connection()
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
            # 🚀 Non-blocking: email is sent in a background thread.
            _send_email_async(msg)

        conn.commit()

        # Invalidate caches so the next GET reflects the new data.
        _cache_invalidate("metrics")
        _cache_invalidate("alerts")

        return {"status": "ok"}

    except Exception as e:
        print("❌ ERROR:", e)
        return {"error": str(e)}

    finally:
        release_connection(conn)


# 🟢 GET METRICS (LATEST ONLY)
@app.get("/metrics")
def get_metrics():
    cached = _cache_get("metrics")
    if cached is not None:
        return cached

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, cpu, memory, disk, timestamp
            FROM metrics
            ORDER BY id DESC
            LIMIT 10
        """)

        rows = cursor.fetchall()
    finally:
        release_connection(conn)

    result = [
        {
            "id": r[0],
            "cpu": float(r[1]),
            "memory": float(r[2]),
            "disk": float(r[3]),
            "time": str(r[4])
        }
        for r in rows
    ]

    _cache_set("metrics", result)
    return result


# 🟡 GET ALERTS
@app.get("/alerts")
def get_alerts():
    cached = _cache_get("alerts")
    if cached is not None:
        return cached

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, message, timestamp
            FROM alerts
            ORDER BY id DESC
            LIMIT 5
        """)

        rows = cursor.fetchall()
    finally:
        release_connection(conn)

    result = [
        {
            "id": r[0],
            "message": r[1],
            "time": str(r[2])
        }
        for r in rows
    ]

    _cache_set("alerts", result)
    return result
