import requests
import psutil
import time

URL = "https://opsguardian.up.railway.app/metrics"

def get_system_metrics():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }

def send_metrics(metrics):
    retries = 3

    for attempt in range(retries):
        try:
            res = requests.post(
                URL,
                json=metrics,
                timeout=15   # 🔥 reduced timeout (faster fail)
            )

            print(f"✅ Sent: {res.status_code}")

            # If backend error, print response
            if res.status_code != 200:
                print("⚠️ Server response:", res.text)

            return

        except requests.exceptions.Timeout:
            print(f"⏳ Timeout (Attempt {attempt+1})")

        except requests.exceptions.ConnectionError:
            print(f"🌐 Connection Error (Attempt {attempt+1})")

        except Exception as e:
            print(f"❌ Error (Attempt {attempt+1}):", e)

        time.sleep(3)  # 🔥 small delay before retry

    print("❌ Failed after retries")


while True:
    metrics = get_system_metrics()

    print("\n📊 SYSTEM METRICS")
    print("CPU:", metrics["cpu"])
    print("Memory:", metrics["memory"])
    print("Disk:", metrics["disk"])

    send_metrics(metrics)

    print("--------------------------------------------------")

    time.sleep(20)   # 🔥 IMPORTANT (reduce load on Railway)