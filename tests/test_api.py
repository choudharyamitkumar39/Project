from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
from src.main import app
from src.api import store

client = TestClient(app)

def setup_function():
    # Clear store before each test for isolation
    store._devices.clear()

def test_register_device():
    response = client.post("/devices", json={"id": "dev-01", "name": "Lab 01"})
    assert response.status_code == 201
    
    devices = store.get_all_devices()
    assert len(devices) == 1
    assert devices[0].id == "dev-01"
    assert devices[0].status == "OFFLINE"

def test_receive_heartbeat():
    client.post("/devices", json={"id": "dev-01", "name": "Lab 01"})
    
    now = datetime.now(timezone.utc).isoformat()
    response = client.post("/devices/dev-01/heartbeat", json={"timestamp": now, "status": "OK"})
    assert response.status_code == 200
    
    dev_response = client.get("/devices/dev-01")
    assert dev_response.json()["status"] == "ONLINE"

def test_heartbeat_device_not_found():
    now = datetime.now(timezone.utc).isoformat()
    response = client.post("/devices/invalid/heartbeat", json={"timestamp": now, "status": "OK"})
    assert response.status_code == 404

def test_30_second_timeout():
    client.post("/devices", json={"id": "dev-01", "name": "Lab 01"})
    
    # Sent 35 seconds ago
    old_time = (datetime.now(timezone.utc) - timedelta(seconds=35)).isoformat()
    client.post("/devices/dev-01/heartbeat", json={"timestamp": old_time, "status": "OK"})
    
    response = client.get("/devices/dev-01")
    assert response.json()["status"] == "OFFLINE"

def test_summary():
    client.post("/devices", json={"id": "dev-01", "name": "Online Dev"})
    client.post("/devices", json={"id": "dev-02", "name": "Offline Dev"})
    
    now = datetime.now(timezone.utc).isoformat()
    client.post("/devices/dev-01/heartbeat", json={"timestamp": now, "status": "OK"})
    
    response = client.get("/summary")
    data = response.json()
    assert data["total"] == 2
    assert data["online"] == 1
    assert data["offline"] == 1
