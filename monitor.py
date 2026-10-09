import psutil
import requests
import os
import socket
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
THRESHOLDS = {
    "cpu": 90,
    "ram": 85,
    "disk": 90,
}
SERVICES = [
    "https://ya.ru",
    "https://github.com",
    "https://google.com",
]


def get_metrics():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    return {
        "cpu": cpu,
        "ram": mem.percent,
        "ram_used_gb": mem.used / (1024 ** 3),
        "ram_total_gb": mem.total / (1024 ** 3),
        "disk": disk.percent,
        "disk_used_gb": disk.used / (1024 ** 3),
        "disk_total_gb": disk.total / (1024 ** 3),
    }


def check_thresholds(metrics):
    alerts = []
    if metrics["cpu"] > THRESHOLDS["cpu"]:
        alerts.append(f"CPU: {metrics['cpu']}% (порог {THRESHOLDS['cpu']}%)")
    if metrics["ram"] > THRESHOLDS["ram"]:
        alerts.append(
            f"RAM: {metrics['ram']}% "
            f"({metrics['ram_used_gb']:.1f}/{metrics['ram_total_gb']:.1f} GB)"
        )
    if metrics["disk"] > THRESHOLDS["disk"]:
        alerts.append(
            f"Диск: {metrics['disk']}% "
            f"({metrics['disk_used_gb']:.1f}/{metrics['disk_total_gb']:.1f} GB)"
        )
    return alerts


def check_services(services):
    alerts = []
    for url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code >= 400:
                alerts.append(f"{url} — код {response.status_code}")
        except requests.exceptions.RequestException:
            alerts.append(f"{url} — недоступен")
    return alerts


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки в Telegram: {e}")
        return False


def main():
    metrics = get_metrics()
    alerts = check_thresholds(metrics)
    service_alerts = check_services(SERVICES)
    alerts.extend(service_alerts)
    

    if alerts:
        hostname = socket.gethostname()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = (
            f"<b>Алерт на сервере</b>\n"
            f"Хост: {hostname}\n"
            f"Время: {now}\n\n"
            + "\n".join(alerts)
        )
        send_telegram(message)
        print(f"[{now}] Отправлен алерт: {len(alerts)} проблем(ы)")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Всё в норме.")


if __name__ == "__main__":
    main()
