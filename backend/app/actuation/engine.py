"""
AirGuard AI - Closed-Loop Smart Home Actuation Engine (Matter & Home Assistant) (v3.0 Section 3.1, 3.2)
Automates smart air purifiers, fresh-air dampers, and motorized windows based on real-time
and ML-forecasted environmental triggers.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database import ActuatorDevice, ActuationLog


class ActuationEngine:
    def __init__(self):
        self.default_actuators = [
            {
                "id": "PURIFIER-LR-01",
                "name": "Living Room Smart HEPA Purifier",
                "room": "Living Room",
                "device_type": "SMART_PURIFIER",
                "protocol": "MATTER",
                "is_online": True,
                "state": "AUTO",
                "fan_speed": "AUTO",
                "damper_position": 50,
                "window_open_pct": 0,
                "auto_mode": True
            },
            {
                "id": "PURIFIER-BR-02",
                "name": "Master Bedroom Smart Purifier",
                "room": "Bedroom",
                "device_type": "SMART_PURIFIER",
                "protocol": "HOME_ASSISTANT",
                "is_online": True,
                "state": "AUTO",
                "fan_speed": "AUTO",
                "damper_position": 50,
                "window_open_pct": 0,
                "auto_mode": True
            },
            {
                "id": "HVAC-DAMPER-01",
                "name": "Central HVAC Fresh-Air Damper",
                "room": "Living Room",
                "device_type": "HVAC_DAMPER",
                "protocol": "MATTER",
                "is_online": True,
                "state": "OPEN",
                "fan_speed": "AUTO",
                "damper_position": 60,
                "window_open_pct": 0,
                "auto_mode": True
            },
            {
                "id": "WINDOW-BR-01",
                "name": "Bedroom Motorized Smart Window",
                "room": "Bedroom",
                "device_type": "MOTORIZED_WINDOW",
                "protocol": "MATTER",
                "is_online": True,
                "state": "CLOSED",
                "fan_speed": "OFF",
                "damper_position": 0,
                "window_open_pct": 0,
                "auto_mode": True
            }
        ]

    async def init_default_actuators(self, session: AsyncSession):
        """Initializes default smart home actuators in the database if not present."""
        for item in self.default_actuators:
            res = await session.execute(
                select(ActuatorDevice).where(ActuatorDevice.id == item["id"])
            )
            existing = res.scalar_one_or_none()
            if not existing:
                actuator = ActuatorDevice(
                    id=item["id"],
                    name=item["name"],
                    room=item["room"],
                    device_type=item["device_type"],
                    protocol=item["protocol"],
                    is_online=item["is_online"],
                    state=item["state"],
                    fan_speed=item["fan_speed"],
                    damper_position=item["damper_position"],
                    window_open_pct=item["window_open_pct"],
                    auto_mode=item["auto_mode"],
                    last_actuated_at=datetime.utcnow()
                )
                session.add(actuator)
        await session.commit()

    async def evaluate_and_actuate(
        self,
        room: str,
        current_pm25: float,
        current_co2: float,
        predicted_pm25_15m: float,
        outdoor_aqi: int,
        session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Evaluates pre-emptive and reactive actuation rules across Matter & Home Assistant devices (Section 3.1).
        """
        res = await session.execute(
            select(ActuatorDevice).where(
                ActuatorDevice.room == room,
                ActuatorDevice.auto_mode == True
            )
        )
        actuators = res.scalars().all()
        actions_taken = []

        now = datetime.utcnow()

        for actuator in actuators:
            # 1. Pre-emptive ML Rule: PM2.5 predicted to exceed 35 ug/m3 in 15 mins
            if actuator.device_type == "SMART_PURIFIER":
                if predicted_pm25_15m >= 45.0 or current_pm25 >= 35.0:
                    if actuator.fan_speed != "BOOST":
                        actuator.fan_speed = "BOOST"
                        actuator.state = "ON"
                        actuator.last_actuated_at = now
                        log = ActuationLog(
                            actuator_id=actuator.id,
                            timestamp=now,
                            trigger_type="PREEMPTIVE_ML",
                            action_taken="Ramp Fan to BOOST",
                            reason=f"Predicted PM2.5 exceeds threshold (+15m: {predicted_pm25_15m} µg/m³)",
                            status="SUCCESS"
                        )
                        session.add(log)
                        actions_taken.append({"actuator_id": actuator.id, "action": "BOOST", "reason": log.reason})
                elif current_pm25 < 12.0 and actuator.fan_speed == "BOOST":
                    actuator.fan_speed = "LOW"
                    actuator.last_actuated_at = now
                    log = ActuationLog(
                        actuator_id=actuator.id,
                        timestamp=now,
                        trigger_type="THRESHOLD_ANOMALY",
                        action_taken="Set Fan to LOW (Nominal)",
                        reason="Air quality restored to safe nominal baseline",
                        status="SUCCESS"
                    )
                    session.add(log)
                    actions_taken.append({"actuator_id": actuator.id, "action": "LOW", "reason": log.reason})

            # 2. Automated Motorized Window & HVAC Damper Rules
            elif actuator.device_type == "MOTORIZED_WINDOW":
                if current_co2 > 1200.0 and outdoor_aqi <= 50:
                    if actuator.window_open_pct < 45:
                        actuator.window_open_pct = 50
                        actuator.state = "OPEN"
                        actuator.last_actuated_at = now
                        log = ActuationLog(
                            actuator_id=actuator.id,
                            timestamp=now,
                            trigger_type="THRESHOLD_ANOMALY",
                            action_taken="Open Window to 50%",
                            reason=f"Stagnant CO2 ({int(current_co2)} ppm) with clean outdoor air (AQI: {outdoor_aqi})",
                            status="SUCCESS"
                        )
                        session.add(log)
                        actions_taken.append({"actuator_id": actuator.id, "action": "OPEN_50%", "reason": log.reason})
                elif outdoor_aqi > 100 or current_pm25 > 40.0:
                    if actuator.window_open_pct > 0:
                        actuator.window_open_pct = 0
                        actuator.state = "CLOSED"
                        actuator.last_actuated_at = now
                        log = ActuationLog(
                            actuator_id=actuator.id,
                            timestamp=now,
                            trigger_type="THRESHOLD_ANOMALY",
                            action_taken="Seal Window (0%)",
                            reason=f"Outdoor particulate pollution hazard (Outdoor AQI: {outdoor_aqi})",
                            status="SUCCESS"
                        )
                        session.add(log)
                        actions_taken.append({"actuator_id": actuator.id, "action": "CLOSE", "reason": log.reason})

            elif actuator.device_type == "HVAC_DAMPER":
                if outdoor_aqi > 100:
                    if actuator.damper_position != 0:
                        actuator.damper_position = 0  # 100% Recirculation
                        actuator.last_actuated_at = now
                        log = ActuationLog(
                            actuator_id=actuator.id,
                            timestamp=now,
                            trigger_type="THRESHOLD_ANOMALY",
                            action_taken="Set HVAC Damper to 0% (Full Recirculation)",
                            reason="Outdoor smoke/smog infiltration detected; sealing envelope",
                            status="SUCCESS"
                        )
                        session.add(log)
                        actions_taken.append({"actuator_id": actuator.id, "action": "RECIRCULATE", "reason": log.reason})

        await session.commit()
        return actions_taken


actuation_engine = ActuationEngine()
