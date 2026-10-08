"""
AirGuard AI - Real-Time WebSocket Streaming Gateway (FR-3.4, NFR-1)
Delivers sub-second telemetry updates and instant push alerts to React dashboards.
"""

import json
from typing import List, Dict, Any, Set
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # Active connections for telemetry stream
        self.telemetry_connections: Set[WebSocket] = set()
        # Active connections for alerts stream
        self.alert_connections: Set[WebSocket] = set()

    async def connect_telemetry(self, websocket: WebSocket):
        await websocket.accept()
        self.telemetry_connections.add(websocket)

    def disconnect_telemetry(self, websocket: WebSocket):
        self.telemetry_connections.discard(websocket)

    async def connect_alerts(self, websocket: WebSocket):
        await websocket.accept()
        self.alert_connections.add(websocket)

    def disconnect_alerts(self, websocket: WebSocket):
        self.alert_connections.discard(websocket)

    async def broadcast_telemetry(self, data: Dict[str, Any]):
        """Broadcasts live sensor payload to all connected clients in < 100ms."""
        if not self.telemetry_connections:
            return

        payload_str = json.dumps(data, default=str)
        dead_sockets = set()
        for connection in self.telemetry_connections:
            try:
                await connection.send_text(payload_str)
            except Exception:
                dead_sockets.add(connection)

        for dead in dead_sockets:
            self.telemetry_connections.discard(dead)

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
