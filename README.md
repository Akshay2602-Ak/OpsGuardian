# 🚀 OpsGuardian

OpsGuardian is a real-time cloud-based system monitoring dashboard that tracks CPU, Memory, and Disk usage from a device and visualizes the data using a modern dashboard.

## 🔥 Features

- Real-time CPU, Memory, and Disk monitoring
- Cloud backend deployed on Railway
- PostgreSQL database storage
- Modern responsive dashboard UI
- Device name support
- Device filter dropdown
- Recent alert section
- Email alert support

## 🛠️ Tech Stack

- Python
- FastAPI
- PostgreSQL
- Railway
- HTML, CSS, JavaScript
- Chart.js
- psutil
- Resend Email API

## 📂 Project Files

```text
main.py
database.py
monitor.py
email_alert.py
dashboard.html
requirements.txt
README.md

## 🚀 How It Works

monitor.py → sends system data → FastAPI backend → PostgreSQL → dashboard.html

---

## ⚙️ Run Monitoring Agent (Local)

```bash
python monitor.py

🌐 Live API

https://opsguardian.up.railway.app

📊 API Endpoints
GET /
POST /metrics
GET /metrics
GET /alerts
GET /devices
GET /test-email