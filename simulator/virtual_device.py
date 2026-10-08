"""
AirGuard AI - Virtual IoT Edge Node Simulator (FR-1, FR-2, NFR-2)
Faithfully emulates ESP32 edge hardware behavior, sensor physics,
offline circular buffering during network dropouts, and burst flush on reconnect.
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
        baseline_hum: float = 46.0
    ):
        self.device_id = device_id
        self.room_name = room_name
        self.backend_url = backend_url
        
        # Current physical atmospheric state
        self.pm2_5 = baseline_pm
        self.pm10 = baseline_pm * 1.4
        self.co2 = baseline_co2
        self.voc = baseline_voc
        self.temperature = baseline_temp
        self.humidity = baseline_hum
        self.pressure = 1013.25

        # Baselines
        self.base_pm = baseline_pm
        self.base_co2 = baseline_co2
        self.base_voc = baseline_voc
        self.base_temp = baseline_temp
        self.base_hum = baseline_hum

        # Offline Buffer Queue (FR-2.3, NFR-2)
        self.is_network_down = False
        self.offline_queue: List[Dict[str, Any]] = []
        self.max_queue_size = 500

        # Active scenario state
        self.active_event: Optional[str] = None
        self.event_remaining_steps = 0

    def trigger_event(self, event_name: str, duration_steps: int = 15):
        """Injects a physical environmental perturbation."""
        self.active_event = event_name.lower()
        self.event_remaining_steps = duration_steps

    def step_physics(self):
        """Simulates 1 discrete time-step of indoor atmospheric evolution."""
        # Brownian random walk
        self.pm2_5 += np.random.normal(0, 0.2)
        self.co2 += np.random.normal(0, 1.2)
        self.voc += np.random.normal(0, 1.0)
        self.temperature += np.random.normal(0, 0.05)
        self.humidity += np.random.normal(0, 0.1)

        # Handling active simulated events
        if self.event_remaining_steps > 0:
            self.event_remaining_steps -= 1
            if self.active_event == "cooking":
                self.pm2_5 += np.random.uniform(4.0, 8.0)
                self.voc += np.random.uniform(15.0, 30.0)
            elif self.active_event == "poor_ventilation":
                self.co2 += np.random.uniform(30.0, 60.0)
                self.voc += np.random.uniform(10.0, 20.0)
            elif self.active_event == "chemical_cleaner":
                self.voc += np.random.uniform(40.0, 70.0)
            elif self.active_event == "open_window":
                # Rapid dilution toward outdoor baseline
                self.pm2_5 += (self.base_pm - self.pm2_5) * 0.25
                self.co2 += (420.0 - self.co2) * 0.30
                self.voc += (self.base_voc - self.voc) * 0.30
        else:
            self.active_event = None
            # Natural relaxation toward room baseline
            self.pm2_5 += (self.base_pm - self.pm2_5) * 0.04
            self.co2 += (self.base_co2 - self.co2) * 0.03
            self.voc += (self.base_voc - self.voc) * 0.04

        # Physical clamping
        self.pm2_5 = max(1.0, self.pm2_5)
        self.pm10 = max(self.pm2_5, self.pm2_5 * 1.35 + np.random.normal(0, 0.4))
        self.co2 = max(390.0, self.co2)
        self.voc = max(10.0, self.voc)
        self.temperature = max(15.0, min(35.0, self.temperature))
        self.humidity = max(20.0, min(95.0, self.humidity))

    def sample_telemetry(self) -> Dict[str, Any]:
        """Samples hardware sensors into JSON telemetry payload."""
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
            "pressure": round(self.pressure, 1)
        }

    def transmit(self) -> bool:
        """Sends reading or queues it during simulated Wi-Fi outage."""
        payload = self.sample_telemetry()

        if self.is_network_down:
            if len(self.offline_queue) < self.max_queue_size:
                self.offline_queue.append(payload)
            return False

        # If network is healthy and there were buffered records, flush them first (FR-2.3)
        if self.offline_queue:
            self._flush_offline_queue()

        # Send current payload
        try:
            resp = requests.post(
                f"{self.backend_url}/telemetry/ingest",
                json=payload,
                timeout=1.5
            )
            return resp.status_code == 200
        except Exception:
            # Network failure: enqueue
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
                # Put back and wait
                self.offline_queue.insert(0, buffered)
                break
