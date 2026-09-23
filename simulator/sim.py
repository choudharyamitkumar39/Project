import time
import requests
import threading
from datetime import datetime, timezone
import random

API_BASE = "http://localhost:8000"

devices = [
    {"id": "device-01", "name": "Lab Device 01", "stop_after": None},
    {"id": "device-02", "name": "Lab Device 02", "stop_after": None},
    {"id": "device-03", "name": "Lab Device 03", "stop_after": None},
    {"id": "device-04", "name": "Lab Device 04", "stop_after": None},
    {"id": "device-05", "name": "Failing Device 05", "stop_after": 20}, # Will stop sending after 20s
]

def register_device(device):
    try:
        response = requests.post(f"{API_BASE}/devices", json={
            "id": device["id"],
            "name": device["name"]
        })
        print(f"[{device['id']}] Registered: {response.status_code}")
    except Exception as e:
        print(f"[{device['id']}] Failed to register: {e}")

def simulate_device(device):
    print(f"[{device['id']}] Starting simulation...")
    register_device(device)
    
    start_time = time.time()
    
    while True:
        elapsed = time.time() - start_time
        if device["stop_after"] and elapsed > device["stop_after"]:
            print(f"[{device['id']}] Stopping heartbeats to simulate OFFLINE status.")
            break
            
        now = datetime.now(timezone.utc).isoformat()
        try:
            response = requests.post(f"{API_BASE}/devices/{device['id']}/heartbeat", json={
                "timestamp": now,
                "status": "OK",
                "cpu_usage": round(random.uniform(10.0, 90.0), 1),
                "signal_strength": round(random.uniform(-90.0, -40.0), 1)
            })
            print(f"[{device['id']}] Heartbeat sent: {response.status_code}")
        except Exception as e:
            print(f"[{device['id']}] Heartbeat failed: {e}")
            
        time.sleep(5)

def main():
    print("Starting Fleet Simulator...")
    print(f"Make sure the API is running on {API_BASE}")
    
    threads = []
    for d in devices:
        t = threading.Thread(target=simulate_device, args=(d,), daemon=True)
        t.start()
        threads.append(t)
        
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Simulator stopped.")

if __name__ == "__main__":
    main()
