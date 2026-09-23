from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DeviceRegister(BaseModel):
    id: str
    name: str

class DeviceHeartbeat(BaseModel):
    timestamp: datetime
    status: str
    cpu_usage: Optional[float] = None
    signal_strength: Optional[float] = None

class DeviceStatus(BaseModel):
    id: str
    name: str
    status: str
    last_heartbeat: Optional[datetime] = None

class FleetSummary(BaseModel):
    total: int
    online: int
    offline: int
