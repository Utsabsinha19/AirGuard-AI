"""
AirGuard AI - MQTT Telemetry Ingestion Subscriber (FR-3.3, NFR-4)
Consumes raw edge telemetry payloads over MQTT and feeds into the calibration,
time-series storage, and WebSocket pipeline.
"""

import json
import asyncio
from datetime import datetime
from typing import Optional
import paho.mqtt.client as mqtt

from backend.app.config import settings
from backend.app.database import async_session_factory
from backend.app.schemas import TelemetryPayload
from backend.app.api.telemetry import ingest_telemetry


class MQTTTelemetrySubscriber:
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.is_connected = False
        self.loop = None

    def start(self, event_loop: asyncio.AbstractEventLoop):
        """Initializes and starts the MQTT client background loop."""
        if not settings.ENABLE_MQTT_SUBSCRIBER:
            print("[MQTT] Subscriber is disabled by configuration (ENABLE_MQTT_SUBSCRIBER=false).")
            return

        self.loop = event_loop
        try:
            self.client = mqtt.Client(
                client_id="AirGuard_Backend_Subscriber",
                protocol=mqtt.MQTTv311
            )
            if settings.MQTT_USERNAME:
                self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message

            print(f"[MQTT] Connecting to broker at {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}...")
            self.client.connect_async(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"[MQTT] Connection warning (MQTT broker may be offline): {e}")

    def stop(self):
        if self.client:
            try:
                self.client.loop_stop()
                self.client.disconnect()
            except Exception:
                pass
            self.is_connected = False

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.is_connected = True
            print(f"[MQTT] Connected successfully. Subscribing to: {settings.MQTT_TELEMETRY_TOPIC}")
            client.subscribe(settings.MQTT_TELEMETRY_TOPIC)
        else:
            print(f"[MQTT] Connection failed with code: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        self.is_connected = False
        print(f"[MQTT] Disconnected from broker (rc={rc})")

    def _on_message(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode("utf-8")
            data = json.loads(payload_str)

            # Extract fields expected by FR-3.3
            parsed_payload = TelemetryPayload(
                device_id=data.get("device_id", "AG-001"),
                timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.utcnow(),
                pm2_5=float(data.get("pm2_5", 0.0)),
                pm10=float(data.get("pm10", 0.0)) if "pm10" in data else None,
                co2=float(data.get("co2", 450.0)),
                voc=float(data.get("voc", 100.0)),
                temperature=float(data.get("temperature", 22.0)),
                humidity=float(data.get("humidity", 45.0)),
                pressure=float(data.get("pressure", 1013.25))
            )

            # Schedule async database ingestion in event loop
            if self.loop and self.loop.is_running():
                asyncio.run_coroutine_threadsafe(self._process_payload(parsed_payload), self.loop)

        except Exception as e:
            print(f"[MQTT] Error handling telemetry message: {e}")

    async def _process_payload(self, payload: TelemetryPayload):
        async with async_session_factory() as session:
            try:
                await ingest_telemetry(payload, session)
            except Exception as e:
                print(f"[MQTT] Database ingestion error: {e}")


mqtt_subscriber = MQTTTelemetrySubscriber()
