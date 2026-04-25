import requests
import psutil
import time

URL = "https://opsguardian.up.railway.app/metrics"

def get_metrics():
    return {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }

while True:
    data = get_metrics()

    print("CPU:", data["cpu"])
    print("Memory:", data["memory"])
    print("Disk:", data["disk"])

    try:
        res = requests.post(URL, json=data, timeout=15)
        print("Sent:", res.status_code)
    except Exception as e:
        print("Network issue:", e)

    print("----------------------")

    time.sleep(10)