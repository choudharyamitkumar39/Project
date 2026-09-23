from fastapi import APIRouter, HTTPException
from typing import List
from .models import DeviceRegister, DeviceHeartbeat, DeviceStatus, FleetSummary
from .store import DeviceStore

router = APIRouter()
store = DeviceStore()

@router.post("/devices", status_code=201)
def register_device(device: DeviceRegister):
    store.register_device(device.id, device.name)
    return {"message": "Device registered successfully"}

@router.post("/devices/{device_id}/heartbeat")
def receive_heartbeat(device_id: str, heartbeat: DeviceHeartbeat):
    success = store.record_heartbeat(device_id, heartbeat)
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"message": "Heartbeat recorded"}

@router.get("/devices", response_model=List[DeviceStatus])
def list_devices():
    return store.get_all_devices()

@router.get("/devices/{device_id}", response_model=DeviceStatus)
def get_device(device_id: str):
    device = store.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.get("/summary", response_model=FleetSummary)
def get_summary():
    return store.get_summary()
