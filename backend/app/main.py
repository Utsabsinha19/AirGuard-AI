"""
AirGuard AI - Main FastAPI Application Server (FR-3.1, FR-3.4)
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.database import init_db
from backend.app.websocket_manager import ws_manager
from backend.app.mqtt.subscriber import mqtt_subscriber

# Import API Routers
from backend.app.api.telemetry import router as telemetry_router
from backend.app.api.devices import router as devices_router
from backend.app.api.predictions import router as predictions_router
from backend.app.api.anomalies import router as anomalies_router
from backend.app.api.alerts import router as alerts_router
from backend.app.api.actions import router as actions_router
from backend.app.api.simulator import router as simulator_router
from backend.app.api.actuation import router as actuation_router
from backend.app.api.health import router as health_router
from backend.app.api.enterprise import router as enterprise_router
from backend.app.ml.predictor_baseline import baseline_predictor
from backend.app.ml.predictor_neural import neural_predictor


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    print("[AirGuard AI] Initializing database tables...")
    await init_db()

    print("[AirGuard AI] Verifying ML model artifacts...")
    baseline_status = "Ready" if baseline_predictor.is_loaded else "Physical Fallback"
    neural_status = "Ready" if neural_predictor.is_loaded else "Not Loaded"
    print(f"  - Phase A Baseline (Gradient Boosting): {baseline_status}")
    print(f"  - Phase B Neural (PyTorch LSTM): {neural_status}")

    loop = asyncio.get_running_loop()
    mqtt_subscriber.start(loop)

    yield

    # Shutdown sequence
    print("[AirGuard AI] Stopping MQTT subscriber...")
    mqtt_subscriber.stop()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="3.0.0",
    description="Autonomous Edge-Intelligent Environmental Health & Closed-Loop Actuation Platform",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(telemetry_router, prefix=settings.API_V1_PREFIX)
app.include_router(devices_router, prefix=settings.API_V1_PREFIX)
app.include_router(predictions_router, prefix=settings.API_V1_PREFIX)
app.include_router(anomalies_router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts_router, prefix=settings.API_V1_PREFIX)
app.include_router(actions_router, prefix=settings.API_V1_PREFIX)
app.include_router(simulator_router, prefix=settings.API_V1_PREFIX)
app.include_router(actuation_router, prefix=settings.API_V1_PREFIX)
app.include_router(health_router, prefix=settings.API_V1_PREFIX)
app.include_router(enterprise_router, prefix=settings.API_V1_PREFIX)


# ---------------------------------------------------------------------------
# WebSocket Gateway Endpoints (FR-3.4, NFR-1 & v3.0 Live Streaming)
# ---------------------------------------------------------------------------

@app.websocket("/ws/telemetry")
@app.websocket("/v3/live")
@app.websocket("/api/v3/live")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """Real-time live telemetry stream (<1s update interval, wss://api.airguard.ai/v3/live)."""
    await ws_manager.connect_telemetry(websocket)
    try:
        while True:
            # Keep-alive ping/pong
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_telemetry(websocket)
    except Exception:
        ws_manager.disconnect_telemetry(websocket)


@app.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    """Real-time priority alert notification push."""
    await ws_manager.connect_alerts(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_alerts(websocket)
    except Exception:
        ws_manager.disconnect_alerts(websocket)


@app.websocket("/v1/live/{device_id}")
@app.websocket("/api/v1/live/{device_id}")
@app.websocket("/v3/live/{device_id}")
@app.websocket("/api/v3/live/{device_id}")
async def websocket_device_live_endpoint(websocket: WebSocket, device_id: str):
    """
    Real-time device-specific atmospheric telemetry live stream
    ws://api.airguard.ai/v1/live/{device_id} & /v3/live/{device_id}.
    """
    await ws_manager.connect_device(device_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_device(device_id, websocket)
    except Exception:
        ws_manager.disconnect_device(device_id, websocket)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "models": {
            "baseline_loaded": baseline_predictor.is_loaded,
            "neural_loaded": neural_predictor.is_loaded
        }
    }


@app.get("/")
async def root():
    return {
        "message": "Welcome to AirGuard AI Backend API",
        "docs_url": "/docs",
        "version": settings.VERSION
    }
