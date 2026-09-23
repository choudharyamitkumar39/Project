import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from .models import DeviceStatus, DeviceHeartbeat

class DeviceStore:
    def __init__(self, timeout_seconds: int = 30):
        self._lock = threading.Lock()
        self._devices: Dict[str, DeviceStatus] = {}
        self._timeout = timedelta(seconds=timeout_seconds)

    def register_device(self, device_id: str, name: str) -> None:
        with self._lock:
            if device_id not in self._devices:
                # Newly registered device has no heartbeat yet, so it is strictly OFFLINE
                self._devices[device_id] = DeviceStatus(
                    id=device_id,
                    name=name,
                    status="OFFLINE",
                    last_heartbeat=None
                )

    def record_heartbeat(self, device_id: str, heartbeat: DeviceHeartbeat) -> bool:
        with self._lock:
            if device_id not in self._devices:
                return False
            
            # Ensure the timestamp has timezone info (assume UTC if naive)
            ts = heartbeat.timestamp
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
                
            device = self._devices[device_id]
            device.last_heartbeat = ts
            device.status = "ONLINE"
            return True

    def _is_online(self, device: DeviceStatus, now: datetime) -> bool:
        if device.last_heartbeat is None:
            return False
        return (now - device.last_heartbeat) <= self._timeout

    def get_all_devices(self) -> List[DeviceStatus]:
        now = datetime.now(timezone.utc)
        result = []
        with self._lock:
            for device in self._devices.values():
                if self._is_online(device, now):
                    device.status = "ONLINE"
                else:
                    device.status = "OFFLINE"
                result.append(device.model_copy())
        return result

    def get_device(self, device_id: str) -> Optional[DeviceStatus]:
        now = datetime.now(timezone.utc)
        with self._lock:
            device = self._devices.get(device_id)
            if not device:
                return None
            
            if self._is_online(device, now):
                device.status = "ONLINE"
            else:
                device.status = "OFFLINE"
            return device.model_copy()

    def get_summary(self) -> dict:
        now = datetime.now(timezone.utc)
        total = 0
        online = 0
        
        with self._lock:
            total = len(self._devices)
            for device in self._devices.values():
                if self._is_online(device, now):
                    online += 1
                    
        return {
            "total": total,
            "online": online,
            "offline": total - online
        }
