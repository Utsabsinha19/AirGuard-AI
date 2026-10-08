"""
AirGuard AI - Real-Time WebSocket Streaming Gateway (FR-3.4, NFR-1)
Delivers sub-second telemetry updates and instant push alerts to React dashboards.
"""

import json
from typing import List, Dict, Any, Set
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # Active connections for global telemetry stream
        self.telemetry_connections: Set[WebSocket] = set()
        # Active connections for alerts stream
        self.alert_connections: Set[WebSocket] = set()
        # Device-specific connections: {device_id: set(WebSockets)}
        self.device_connections: Dict[str, Set[WebSocket]] = {}

    async def connect_telemetry(self, websocket: WebSocket):
        await websocket.accept()
        self.telemetry_connections.add(websocket)

    def disconnect_telemetry(self, websocket: WebSocket):
        self.telemetry_connections.discard(websocket)

    async def connect_device(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        if device_id not in self.device_connections:
            self.device_connections[device_id] = set()
        self.device_connections[device_id].add(websocket)

    def disconnect_device(self, device_id: str, websocket: WebSocket):
        if device_id in self.device_connections:
            self.device_connections[device_id].discard(websocket)
            if not self.device_connections[device_id]:
                del self.device_connections[device_id]

    async def connect_alerts(self, websocket: WebSocket):
        await websocket.accept()
        self.alert_connections.add(websocket)

    def disconnect_alerts(self, websocket: WebSocket):
        self.alert_connections.discard(websocket)

    async def broadcast_telemetry(self, data: Dict[str, Any]):
        """Broadcasts live sensor payload to all connected clients and device-specific subscribers in < 100ms."""
        payload_str = json.dumps(data, default=str)

        # Global subscribers
        dead_global = set()
        for connection in self.telemetry_connections:
            try:
                await connection.send_text(payload_str)
            except Exception:
                dead_global.add(connection)
        for dead in dead_global:
            self.telemetry_connections.discard(dead)

        # Device-specific subscribers (e.g. /v1/live/{device_id})
        device_id = data.get("device_id")
        if device_id and device_id in self.device_connections:
            dead_dev = set()
            for connection in self.device_connections[device_id]:
                try:
                    await connection.send_text(payload_str)
                except Exception:
                    dead_dev.add(connection)
            for dead in dead_dev:
                self.device_connections[device_id].discard(dead)

    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        """Pushes instantaneous priority alert to UI clients."""
        if not self.alert_connections:
            return

        payload_str = json.dumps(alert_data, default=str)
        dead_sockets = set()
        for connection in self.alert_connections:
            try:
                await connection.send_text(payload_str)
            except Exception:
                dead_sockets.add(connection)

        for dead in dead_sockets:
            self.alert_connections.discard(dead)


ws_manager = ConnectionManager()
