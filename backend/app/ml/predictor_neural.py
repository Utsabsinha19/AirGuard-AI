"""
AirGuard AI - Phase B Deep Sequence Predictive Engine (FR-4.2)
Multi-layer PyTorch Neural Architecture (LSTM) trained on multivariate time-series tensors
to capture long-range temporal dependencies and non-linear decay dynamics.
"""

import os
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, List, Optional
from backend.app.ml.calibration import compute_comprehensive_aqi


class AirGuardSeqLSTM(nn.Module):
    def __init__(self, input_dim: int = 5, hidden_dim: int = 64, num_layers: int = 2, num_horizons: int = 4, num_targets: int = 3):
        super(AirGuardSeqLSTM, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.num_horizons = num_horizons
        self.num_targets = num_targets

        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.15 if num_layers > 1 else 0.0
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, num_horizons * num_targets)
        )

    def forward(self, x):
        # x shape: (batch_size, seq_len, input_dim)
        lstm_out, _ = self.lstm(x)
        # take last timestep output
        last_out = lstm_out[:, -1, :]
        out = self.fc(last_out)
        return out.view(-1, self.num_horizons, self.num_targets)


class NeuralPredictor:
    def __init__(self, models_dir: Optional[str] = None):
        if models_dir is None:
            models_dir = os.path.join(os.path.dirname(__file__), "models")
        self.models_dir = models_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.horizons = [15, 30, 60, 360]
        self.is_loaded = False
        self.load_model()

    def load_model(self):
        model_path = os.path.join(self.models_dir, "lstm_model.pt")
        if os.path.exists(model_path):
            try:
                self.model = AirGuardSeqLSTM(input_dim=5, hidden_dim=64, num_layers=2)
                state_dict = torch.load(model_path, map_location=self.device)
                self.model.load_state_dict(state_dict)
                self.model.to(self.device)
                self.model.eval()
                self.is_loaded = True
            except Exception as e:
                print(f"[NeuralPredictor] Warning: could not load PyTorch model: {e}")
                self.is_loaded = False

    def predict_sequence(
        self,
        recent_readings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Takes recent history (last 10-30 readings) and outputs predictions for +15m, +30m, +1h, +6h.
        """
        if not self.is_loaded or self.model is None or len(recent_readings) < 5:
            # Fallback to baseline
            from backend.app.ml.predictor_baseline import baseline_predictor
            current = recent_readings[-1] if recent_readings else {}
            preds = baseline_predictor.predict_horizons(current, recent_readings)
            for p in preds:
                p["model_type"] = "Baseline_Fallback"
            return preds

        # Prepare tensor (batch_size=1, seq_len, 5)
        # Features: [pm2_5, co2/100, voc/10, temp, humidity]
        seq = []
        for r in recent_readings[-30:]:
            pm = float(r.get("pm2_5", 10.0) or 10.0)
            co2 = float(r.get("co2", 600.0) or 600.0) / 100.0
            voc = float(r.get("voc", 100.0) or 100.0) / 10.0
            temp = float(r.get("temperature", 22.0) or 22.0)
            hum = float(r.get("humidity", 45.0) or 45.0)
            seq.append([pm, co2, voc, temp, hum])

        # Pad if shorter than 30
        while len(seq) < 30:
            seq.insert(0, seq[0])

        tensor_in = torch.tensor([seq], dtype=torch.float32).to(self.device)
        with torch.no_grad():
            out = self.model(tensor_in).cpu().numpy()[0]  # shape: (4, 3)

        predictions = []
        for idx, h in enumerate(self.horizons):
            pred_pm = max(0.0, round(float(out[idx, 0]), 1))
            pred_co2 = max(380.0, round(float(out[idx, 1]) * 100.0, 0))
            pred_voc = max(0.0, round(float(out[idx, 2]) * 10.0, 1))

            ci_spread = max(1.5, pred_pm * 0.12 * (1.0 + np.sqrt(h / 60.0) * 0.25))
            conf_lower = max(0.0, round(pred_pm - ci_spread, 1))
            conf_upper = round(pred_pm + ci_spread, 1)

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
                "model_type": "PyTorch_LSTM_PhaseB"
            })

        return predictions


neural_predictor = NeuralPredictor()
