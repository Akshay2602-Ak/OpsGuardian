import requests
import psutil
import time

def get_system_metrics():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }

while True:
    metrics = get_system_metrics()

    print("CPU:", metrics["cpu"])
    print("Memory:", metrics["memory"])
    print("Disk:", metrics["disk"])

    try:
        res = requests.post(
        "https://opsguardian-production.up.railway.app/metrics",
        json=metrics,
        timeout=5
    )
        print("✅ Sent to backend:", res.status_code)
    except Exception as e:
        print("❌ Error:", e)

    print("----------------------")

    time.sleep(5)