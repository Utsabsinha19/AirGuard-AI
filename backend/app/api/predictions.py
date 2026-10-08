"""
AirGuard AI - Predictive Forecasting API (FR-4.1, FR-4.2)
Delivers trajectories for +15m, +30m, +1h, and +6h horizons with confidence intervals.
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.database import get_db, Telemetry, Device
from backend.app.schemas import PredictionResponse, HorizonPrediction
from backend.app.ml.predictor_baseline import baseline_predictor
from backend.app.ml.predictor_neural import neural_predictor

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/{device_id}", response_model=PredictionResponse)
async def get_predictions(
    device_id: str,
    model_type: str = Query("baseline", pattern="^(baseline|neural)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    Computes and returns air quality trajectories for +15m, +30m, +1h, and +6h.
    Uses either Phase A (Gradient Boosting) or Phase B (PyTorch LSTM).
    """
    # Fetch recent telemetry history for feature engineering (up to 30 past points)
    query = await db.execute(
        select(Telemetry)
        .where(Telemetry.device_id == device_id)
        .order_by(desc(Telemetry.timestamp))
        .limit(30)
    )
    records = query.scalars().all()

    if not records:
        # Fallback default readings if device has just been turned on
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

    # Model inference
    if model_type == "neural" and neural_predictor.is_loaded:
        raw_preds = neural_predictor.predict_sequence(recent_list)
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
