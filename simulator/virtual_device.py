"""
AirGuard AI - Virtual IoT Edge Node Simulator (Enhanced, Section 2.1)
Simulates extended sensors:
- BMP280 Barometric Pressure & Weather Trends
- Ambient Lux Lighting & Circadian Oscillations
- Acoustic Noise dB & Human Activity Levels
- Li-Po Battery Monitoring & Discharge
- GPS Coordinates for Spatial / Mobile Mapping
"""

import time
import requests
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


class VirtualEdgeNode:
    def __init__(
        self,
        device_id: str,
        room_name: str,
        backend_url: str = "http://127.0.0.1:8000/api",
        baseline_pm: float = 8.0,
        baseline_co2: float = 550.0,
        baseline_voc: float = 90.0,
        baseline_temp: float = 22.0,
        baseline_hum: float = 46.0,
        latitude: float = 37.7749,
        longitude: float = -122.4194
    ):
        self.device_id = device_id
        self.room_name = room_name
        self.backend_url = backend_url
        
        self.pm2_5 = baseline_pm
        self.pm10 = baseline_pm * 1.4
        self.co2 = baseline_co2
        self.voc = baseline_voc
        self.temperature = baseline_temp
        self.humidity = baseline_hum
        self.pressure = 1013.25
        self.ambient_light = 180.0
        self.noise_level = 42.0
        self.battery_pct = 96
        self.latitude = latitude
        self.longitude = longitude

        self.base_pm = baseline_pm
        self.base_co2 = baseline_co2
        self.base_voc = baseline_voc
        self.base_temp = baseline_temp
        self.base_hum = baseline_hum
        self.base_pressure = 1013.25

        self.is_network_down = False
        self.offline_queue: List[Dict[str, Any]] = []
        self.max_queue_size = 500

        self.active_event: Optional[str] = None
        self.event_remaining_steps = 0

    def trigger_event(self, event_name: str, duration_steps: int = 15):
        self.active_event = event_name.lower()
        self.event_remaining_steps = duration_steps

    def step_physics(self):
        self.pm2_5 += np.random.normal(0, 0.2)
        self.co2 += np.random.normal(0, 1.2)
        self.voc += np.random.normal(0, 1.0)
        self.temperature += np.random.normal(0, 0.05)
        self.humidity += np.random.normal(0, 0.1)
        self.pressure += np.random.normal(0, 0.08)
        self.noise_level = 40.0 + np.random.normal(0, 2.5)

        # Ambient light diurnal cycle
        hour = datetime.utcnow().hour
        is_day = 6 <= hour <= 20
        self.ambient_light = 240.0 + np.random.normal(0, 15.0) if is_day else 15.0 + np.random.normal(0, 3.0)

        # Handling simulated events
        if self.event_remaining_steps > 0:
            self.event_remaining_steps -= 1
            if self.active_event == "cooking":
                self.pm2_5 += np.random.uniform(4.0, 8.0)
                self.voc += np.random.uniform(15.0, 30.0)
                self.noise_level += 18.0
            elif self.active_event == "poor_ventilation":
                self.co2 += np.random.uniform(30.0, 60.0)
                self.voc += np.random.uniform(10.0, 20.0)
            elif self.active_event == "chemical_cleaner":
                self.voc += np.random.uniform(40.0, 70.0)
                self.noise_level = 38.0  # silent
            elif self.active_event == "high_occupancy":
                self.co2 += np.random.uniform(40.0, 80.0)
                self.voc += np.random.uniform(15.0, 30.0)
                self.noise_level = 72.0 + np.random.normal(0, 4.0)  # loud social noise
            elif self.active_event == "weather_inversion":
                self.pressure = 1004.0 - np.random.uniform(1.0, 4.0)  # low pressure
                self.pm2_5 += np.random.uniform(3.0, 6.0)
            elif self.active_event == "open_window":
                self.pm2_5 += (self.base_pm - self.pm2_5) * 0.25
                self.co2 += (420.0 - self.co2) * 0.30
                self.voc += (self.base_voc - self.voc) * 0.30
        else:
            self.active_event = None
            self.pm2_5 += (self.base_pm - self.pm2_5) * 0.04
            self.co2 += (self.base_co2 - self.co2) * 0.03
            self.voc += (self.base_voc - self.voc) * 0.04
            self.pressure += (self.base_pressure - self.pressure) * 0.05

        self.pm2_5 = max(1.0, self.pm2_5)
        self.pm10 = max(self.pm2_5, self.pm2_5 * 1.35 + np.random.normal(0, 0.4))
        self.co2 = max(390.0, self.co2)
        self.voc = max(10.0, self.voc)
        self.noise_level = max(35.0, min(95.0, self.noise_level))

    def sample_telemetry(self) -> Dict[str, Any]:
        self.step_physics()
        return {
            "device_id": self.device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "pm2_5": round(self.pm2_5, 1),
            "pm10": round(self.pm10, 1),
            "co2": round(self.co2, 0),
            "voc": round(self.voc, 1),
            "temperature": round(self.temperature, 1),
            "humidity": round(self.humidity, 1),
            "pressure": round(self.pressure, 1),
            "ambient_light": round(self.ambient_light, 1),
            "noise_level": round(self.noise_level, 1),
            "battery_pct": self.battery_pct,
            "latitude": self.latitude,
            "longitude": self.longitude
        }

    def transmit(self) -> bool:
        payload = self.sample_telemetry()

        if self.is_network_down:
            if len(self.offline_queue) < self.max_queue_size:
                self.offline_queue.append(payload)
            return False

        if self.offline_queue:
            self._flush_offline_queue()

        try:
            resp = requests.post(
                f"{self.backend_url}/telemetry/ingest",
                json=payload,
                timeout=1.5
            )
            return resp.status_code == 200
        except Exception:
            self.offline_queue.append(payload)
            return False

    def _flush_offline_queue(self):
        print(f"[{self.device_id}] Reconnected! Flushing {len(self.offline_queue)} queued records to backend...")
        while self.offline_queue:
            buffered = self.offline_queue.pop(0)
            try:
                requests.post(
                    f"{self.backend_url}/telemetry/ingest",
                    json=buffered,
                    timeout=1.5
                )
            except Exception:
                self.offline_queue.insert(0, buffered)
                break
