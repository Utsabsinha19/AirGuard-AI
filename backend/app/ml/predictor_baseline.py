"""
AirGuard AI - Phase A Predictive Engine (FR-4.2, NFR-3)
Baseline Machine Learning Model Suite utilizing Gradient Boosting / Random Forest
to forecast air quality trajectories across +15m, +30m, +1h, and +6h horizons with confidence intervals.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from backend.app.ml.calibration import compute_comprehensive_aqi


class BaselinePredictor:
    def __init__(self, models_dir: Optional[str] = None):
        if models_dir is None:
            models_dir = os.path.join(os.path.dirname(__file__), "models")
        self.models_dir = models_dir
        self.models = {}  # {horizon_name: model}
        self.scaler = None
        self.feature_names = []
        self.horizons = [15, 30, 60, 360]  # in minutes
        self.is_loaded = False
        self.load_models()

    def load_models(self):
        """Loads pre-trained model artifacts if available."""
        baseline_file = os.path.join(self.models_dir, "baseline_models.joblib")
        scaler_file = os.path.join(self.models_dir, "scaler.joblib")
        features_file = os.path.join(self.models_dir, "feature_names.json")

        if os.path.exists(baseline_file) and os.path.exists(scaler_file):
            try:
                self.models = joblib.load(baseline_file)
                self.scaler = joblib.load(scaler_file)
                if os.path.exists(features_file):
                    import json
                    with open(features_file, "r") as f:
                        self.feature_names = json.load(f)
                self.is_loaded = True
            except Exception as e:
                print(f"[BaselinePredictor] Warning: could not load model artifacts: {e}")
                self.is_loaded = False

    def predict_horizons(
        self,
        current_reading: Dict[str, Any],
        recent_history: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Forecasts +15m, +30m, +1h (60m), and +6h (360m) future states.
        Returns a list of prediction dictionaries with:
        - horizon_mins
        - predicted_pm2_5
        - predicted_co2
        - predicted_voc
        - predicted_aqi
        - aqi_category
        - confidence_lower
        - confidence_upper
        """
        pm_cur = float(current_reading.get("pm2_5", 12.0) or 12.0)
        co2_cur = float(current_reading.get("co2", 650.0) or 650.0)
        voc_cur = float(current_reading.get("voc", 120.0) or 120.0)
        temp_cur = float(current_reading.get("temperature", 22.0) or 22.0)
        humidity_cur = float(current_reading.get("humidity", 45.0) or 45.0)

        # Trend estimation from history if available
        pm_trend = 0.0
        co2_trend = 0.0
        if recent_history and len(recent_history) >= 5:
            # calculate 5-minute derivative
            prev_pm = float(recent_history[-5].get("pm2_5", pm_cur) or pm_cur)
            prev_co2 = float(recent_history[-5].get("co2", co2_cur) or co2_cur)
            pm_trend = (pm_cur - prev_pm) / 5.0
            co2_trend = (co2_cur - prev_co2) / 5.0

        predictions = []

        for h in self.horizons:
            key = f"h_{h}"
            if self.is_loaded and key in self.models and self.scaler:
                try:
                    # Construct feature vector as DataFrame with feature names
                    feat_dict = {
                        "pm2_5": [pm_cur], "co2": [co2_cur], "voc": [voc_cur],
                        "temperature": [temp_cur], "humidity": [humidity_cur],
                        "pm_trend": [pm_trend], "co2_trend": [co2_trend],
                        "sin_hour": [0.0], "cos_hour": [1.0]
                    }
                    df_feats = pd.DataFrame({fn: feat_dict.get(fn, [0.0]) for fn in self.feature_names})
                    x_scaled = self.scaler.transform(df_feats)
                    model_bundle = self.models[key]
                    
                    pred_pm = float(model_bundle["pm2_5"].predict(x_scaled)[0])
                    pred_co2 = float(model_bundle["co2"].predict(x_scaled)[0])
                    pred_voc = float(model_bundle["voc"].predict(x_scaled)[0])
                    std_pm = float(model_bundle.get("std_pm", max(2.0, pred_pm * 0.12)))
                except Exception as ex:
                    # Fallback to physical model
                    pred_pm, pred_co2, pred_voc, std_pm = self._physics_forecast(
                        pm_cur, co2_cur, voc_cur, pm_trend, co2_trend, h
                    )
            else:
                pred_pm, pred_co2, pred_voc, std_pm = self._physics_forecast(
                    pm_cur, co2_cur, voc_cur, pm_trend, co2_trend, h
                )

            # Post-process bounds
            pred_pm = max(0.0, round(pred_pm, 1))
            pred_co2 = max(380.0, round(pred_co2, 0))
            pred_voc = max(0.0, round(pred_voc, 1))

            # 95% Confidence Interval (approx 1.96 * std)
            ci_spread = max(1.5, std_pm * 1.96 * (1.0 + np.sqrt(h / 60.0) * 0.3))
            conf_lower = max(0.0, round(pred_pm - ci_spread, 1))
            conf_upper = round(pred_pm + ci_spread, 1)

            # Compute predicted AQI
            aqi_res = compute_comprehensive_aqi(pm25=pred_pm, co2=pred_co2, voc=pred_voc)

            predictions.append({
                "horizon_mins": h,
                "horizon_label": f"+{h}m" if h < 60 else f"+{h//60}h",
                "predicted_pm2_5": pred_pm,
                "predicted_co2": int(pred_co2),
                "predicted_voc": int(pred_voc),
                "predicted_aqi": aqi_res["aqi"],
                "aqi_category": aqi_res["category"],
                "aqi_color": aqi_res["color"],
                "dominant_pollutant": aqi_res["dominant_pollutant"],
                "confidence_lower": conf_lower,
                "confidence_upper": conf_upper,
                "model_type": "GradientBoosting_PhaseA" if self.is_loaded else "PhysicalDiffusion_Model"
            })

        return predictions

    def _physics_forecast(
        self,
        pm: float,
        co2: float,
        voc: float,
        pm_trend: float,
        co2_trend: float,
        horizon_mins: int
    ):
        """
        Physics-based baseline implementing mass-balance room decay and baseline convergence.
        Particulates naturally settle with half-life ~45 mins in closed rooms.
        CO2 accumulates with occupancy or decays toward 420 ppm background.
        """
        # Baseline target levels (clean room)
        baseline_pm = 8.0
        baseline_co2 = 500.0
        baseline_voc = 100.0

        t_hours = horizon_mins / 60.0

        # Short term momentum + exponential decay back to baseline equilibrium
        if pm > baseline_pm:
            # Decay rate lambda approx 0.8 per hour for indoor particulate deposition
            decay = np.exp(-0.75 * t_hours)
            pred_pm = baseline_pm + (pm - baseline_pm + pm_trend * min(horizon_mins, 15)) * decay
        else:
            pred_pm = pm + pm_trend * min(horizon_mins, 15) * 0.5

        # CO2 dynamics (decay or persistent elevation)
        if co2_trend > 0:
            # Active accumulation
            pred_co2 = co2 + co2_trend * min(horizon_mins, 45) * 0.7
        else:
            decay_co2 = np.exp(-0.4 * t_hours)
            pred_co2 = baseline_co2 + (co2 - baseline_co2) * decay_co2

        decay_voc = np.exp(-0.6 * t_hours)
        pred_voc = baseline_voc + (voc - baseline_voc) * decay_voc

        std_pm = max(1.8, pred_pm * 0.15)
        return pred_pm, pred_co2, pred_voc, std_pm


baseline_predictor = BaselinePredictor()
