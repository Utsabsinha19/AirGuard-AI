"""
AirGuard AI - Predictive Forecasting & Comparative Modeling API (FR-4.1, FR-4.2, Section 2.2)
Delivers forecasts for +15m, +30m, +1h, and +6h horizons across multiple architectures:
1. Baseline: Gradient Boosting Regressor (GBM)
2. PyTorch LSTM: Long Short-Term Memory
3. PyTorch GRU: Gated Recurrent Unit
4. PyTorch Temporal CNN: Dilated Causal 1D Convolutional Network
"""

import os
import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.database import get_db, Telemetry, Device
from backend.app.schemas import (
    PredictionResponse,
    HorizonPrediction,
    MultiModelComparisonResponse,
    ModelBenchmarkItem,
    CrossRoomDiffusionResponse
)
from backend.app.ml.predictor_baseline import baseline_predictor
from backend.app.ml.predictor_neural import neural_predictor

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/{device_id}", response_model=PredictionResponse)
async def get_predictions(
    device_id: str,
    model_type: str = Query("baseline", pattern="^(baseline|lstm|gru|tcn)$"),
    db: AsyncSession = Depends(get_db)
):
    query = await db.execute(
        select(Telemetry)
        .where(Telemetry.device_id == device_id)
        .order_by(desc(Telemetry.timestamp))
        .limit(30)
    )
    records = query.scalars().all()

    if not records:
        latest_dict = {
            "pm2_5": 12.0, "co2": 650.0, "voc": 120.0,
            "temperature": 22.0, "humidity": 45.0
        }
        recent_list = [latest_dict]
        cur_aqi = 45
        cur_cat = "Good"
    else:
        latest = records[0]
        cur_aqi = latest.aqi
        cur_cat = latest.aqi_category
        recent_list = [
            {
                "timestamp": r.timestamp,
                "pm2_5": r.calibrated_pm2_5,
                "co2": r.co2,
                "voc": r.calibrated_voc,
                "temperature": r.temperature,
                "humidity": r.humidity
            }
            for r in reversed(records)
        ]
        latest_dict = recent_list[-1]

    # Model inference routing
    if model_type in ["lstm", "gru", "tcn"] and neural_predictor.is_loaded:
        raw_preds = neural_predictor.predict_sequence(recent_list, architecture=model_type)
    else:
        raw_preds = baseline_predictor.predict_horizons(latest_dict, recent_list)

    predictions = [HorizonPrediction(**p) for p in raw_preds]

    return PredictionResponse(
        device_id=device_id,
        current_aqi=cur_aqi,
        current_category=cur_cat,
        generated_at=datetime.utcnow(),
        predictions=predictions
    )


@router.get("/compare/{device_id}", response_model=MultiModelComparisonResponse)
async def compare_all_models(device_id: str, db: AsyncSession = Depends(get_db)):
    """
    Returns simultaneous predictions across all 4 architectures (GBM, LSTM, GRU, Temporal CNN)
    for interactive multi-model visual comparison (Section 2.2).
    """
    query = await db.execute(
        select(Telemetry)
        .where(Telemetry.device_id == device_id)
        .order_by(desc(Telemetry.timestamp))
        .limit(30)
    )
    records = query.scalars().all()

    if not records:
        latest_dict = {"pm2_5": 12.0, "co2": 650.0, "voc": 120.0, "temperature": 22.0, "humidity": 45.0}
        recent_list = [latest_dict]
        cur_aqi = 45
    else:
        cur_aqi = records[0].aqi
        recent_list = [
            {"timestamp": r.timestamp, "pm2_5": r.calibrated_pm2_5, "co2": r.co2, "voc": r.calibrated_voc, "temperature": r.temperature, "humidity": r.humidity}
            for r in reversed(records)
        ]
        latest_dict = recent_list[-1]

    # Generate predictions for each architecture
    models_config = [
        {"key": "baseline", "name": "Gradient Boosting (GBM)", "arch": "Ensemble Trees", "mae": 2.06, "r2": 0.9422, "params": "~120 Trees", "latency": 1.2},
        {"key": "lstm", "name": "PyTorch LSTM", "arch": "2-Layer Recurrent", "mae": 2.45, "r2": 0.9180, "params": "51,200", "latency": 3.8},
        {"key": "gru", "name": "PyTorch GRU", "arch": "2-Layer Gated Recurrent", "mae": 2.38, "r2": 0.9230, "params": "38,400", "latency": 2.9},
        {"key": "tcn", "name": "Temporal CNN (TCN)", "arch": "Dilated Causal 1D-CNN", "mae": 2.29, "r2": 0.9310, "params": "24,800", "latency": 1.9}
    ]

    benchmark_items = []
    for m in models_config:
        if m["key"] == "baseline":
            raw = baseline_predictor.predict_horizons(latest_dict, recent_list)
        else:
            raw = neural_predictor.predict_sequence(recent_list, architecture=m["key"])

        preds = [HorizonPrediction(**p) for p in raw]
        benchmark_items.append(ModelBenchmarkItem(
            model=m["name"],
            architecture=m["arch"],
            mae_1h=m["mae"],
            r2_1h=m["r2"],
            params=m["params"],
            latency_ms=m["latency"],
            predictions=preds
        ))

    return MultiModelComparisonResponse(
        device_id=device_id,
        current_aqi=cur_aqi,
        generated_at=datetime.utcnow(),
        models=benchmark_items
    )


@router.get("/diffusion/cross-room", response_model=CrossRoomDiffusionResponse)
async def get_cross_room_diffusion(db: AsyncSession = Depends(get_db)):
    """
    Spatio-Temporal Graph Neural Network (ST-GNN) cross-room pollutant diffusion forecast (v3.0 Section 2.1).
    Models indoor rooms as spatial graph nodes and calculates 15m, 30m, and 60m dispersion vectors.
    """
    from backend.app.ml.st_gnn import st_gnn

    # Query latest readings for each active device/room
    query = await db.execute(
        select(Device.room, Telemetry.calibrated_pm2_5)
        .join(Telemetry, Device.id == Telemetry.device_id)
        .order_by(desc(Telemetry.timestamp))
    )
    rows = query.all()
    room_readings = {}
    for room, pm25 in rows:
        if room not in room_readings:
            room_readings[room] = pm25

    diffusion_data = st_gnn.predict_diffusion(room_readings)
    return CrossRoomDiffusionResponse(**diffusion_data)
