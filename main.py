from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 In-memory storage (NO DB)
metrics_data = []
alerts_data = []


@app.get("/")
def home():
    return {"message": "OpsGuardian Backend is Running 🚀"}


@app.post("/metrics")
def receive_metrics(data: dict):
    try:
        cpu = data.get("cpu")
        memory = data.get("memory")
        disk = data.get("disk")

        entry = {
            "cpu": cpu,
            "memory": memory,
            "disk": disk
        }

        metrics_data.insert(0, entry)

        if len(metrics_data) > 10:
            metrics_data.pop()

        # 🔥 Alert logic (only one)
        msg = None
        if cpu > 50:
            msg = f"High CPU: {cpu}%"
        elif memory > 70:
            msg = f"High Memory: {memory}%"
        elif disk > 80:
            msg = f"Disk Full: {disk}%"

        if msg:
            alerts_data.insert(0, {"message": msg})
            if len(alerts_data) > 5:
                alerts_data.pop()

        return {"status": "ok"}

    except Exception as e:
        return {"error": str(e)}


@app.get("/metrics")
def get_metrics():
    return metrics_data


@app.get("/alerts")
def get_alerts():
    return alerts_data