import sqlite3
import threading
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from .models import DeviceStatus, DeviceHeartbeat
from .config import TIMEOUT_SECONDS, DB_PATH
from .logger import logger

class DeviceStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._timeout = timedelta(seconds=TIMEOUT_SECONDS)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        with self._lock:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    status TEXT,
                    last_heartbeat TEXT
                )
            ''')
            self.conn.commit()

    def register_device(self, device_id: str, name: str) -> None:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM devices WHERE id = ?", (device_id,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO devices (id, name, status, last_heartbeat) VALUES (?, ?, ?, ?)",
                    (device_id, name, "OFFLINE", None)
                )
                self.conn.commit()
                logger.info(f"Registered new device: {device_id}")

    def record_heartbeat(self, device_id: str, heartbeat: DeviceHeartbeat) -> bool:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM devices WHERE id = ?", (device_id,))
            if not cursor.fetchone():
                return False
            
            ts = heartbeat.timestamp
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
                
            cursor.execute(
                "UPDATE devices SET last_heartbeat = ?, status = 'ONLINE' WHERE id = ?",
                (ts.isoformat(), device_id)
            )
            self.conn.commit()
            logger.info(f"Heartbeat received for {device_id}")
            return True

    def _parse_device(self, row, now: datetime) -> DeviceStatus:
        dev_id, name, _, last_hb_str = row
        last_hb = datetime.fromisoformat(last_hb_str) if last_hb_str else None
        
        is_online = False
        if last_hb:
            is_online = (now - last_hb) <= self._timeout
        
        return DeviceStatus(
            id=dev_id,
            name=name,
            status="ONLINE" if is_online else "OFFLINE",
            last_heartbeat=last_hb
        )

    def get_all_devices(self, status_filter: Optional[str] = None) -> List[DeviceStatus]:
        now = datetime.now(timezone.utc)
        results = []
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name, status, last_heartbeat FROM devices")
            for row in cursor.fetchall():
                dev = self._parse_device(row, now)
                if status_filter:
                    if dev.status.upper() == status_filter.upper():
                        results.append(dev)
                else:
                    results.append(dev)
        return results

    def get_device(self, device_id: str) -> Optional[DeviceStatus]:
        now = datetime.now(timezone.utc)
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name, status, last_heartbeat FROM devices WHERE id = ?", (device_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._parse_device(row, now)

    def get_summary(self) -> dict:
        devices = self.get_all_devices()
        total = len(devices)
        online = sum(1 for d in devices if d.status == "ONLINE")
        return {
            "total": total,
            "online": online,
            "offline": total - online
        }
    
    def close(self):
        self.conn.close()
        logger.info("Database connection closed gracefully.")
