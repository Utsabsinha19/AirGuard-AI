"""
AirGuard AI - Multi-Sensor Anomaly Detection & Root-Cause Diagnostic Engine (FR-4.3)
Answers core target questions:
- "Is this unusual?" -> Baseline deviation and z-score spike detection
- "Why is it getting worse?" -> Multi-sensor cross-correlation root cause identification
- "What should I do?" -> Actionable, localized remediation guidance
"""

from typing import Dict, Any, List, Optional
import numpy as np


class AnomalyEngine:
    def __init__(self):
        # Baseline reference parameters for typical indoor residential/office spaces
        self.default_baselines = {
            "pm2_5": {"median": 10.0, "std": 5.0, "p95": 25.0},
            "pm10": {"median": 18.0, "std": 8.0, "p95": 40.0},
            "co2": {"median": 650.0, "std": 120.0, "p95": 950.0},
            "voc": {"median": 120.0, "std": 45.0, "p95": 250.0},
            "temperature": {"median": 22.0, "std": 2.0, "p95": 26.0},
            "humidity": {"median": 45.0, "std": 8.0, "p95": 65.0}
        }

    def detect_anomalies_and_diagnose(
        self,
        current_reading: Dict[str, float],
        historical_readings: Optional[List[Dict[str, float]]] = None
    ) -> Dict[str, Any]:
        """
        Analyzes current reading against baseline and historical trends.
        Performs multi-sensor cross-correlation to pinpoint root cause.
        """
        # Calculate dynamic baselines if historical data is provided, else fallback to standard
        baselines = self._calculate_baselines(historical_readings)

        pm25 = float(current_reading.get("pm2_5", 0.0) or 0.0)
        pm10 = float(current_reading.get("pm10", pm25 * 1.5) or 0.0)
        co2 = float(current_reading.get("co2", 600.0) or 600.0)
        voc = float(current_reading.get("voc", 100.0) or 100.0)
        temp = float(current_reading.get("temperature", 22.0) or 22.0)
        humidity = float(current_reading.get("humidity", 45.0) or 45.0)

        # Standard z-scores relative to baseline
        z_pm25 = max(0.0, (pm25 - baselines["pm2_5"]["median"]) / max(1.0, baselines["pm2_5"]["std"]))
        z_co2 = max(0.0, (co2 - baselines["co2"]["median"]) / max(1.0, baselines["co2"]["std"]))
        z_voc = max(0.0, (voc - baselines["voc"]["median"]) / max(1.0, baselines["voc"]["std"]))

        is_pm_elevated = pm25 > 25.0 or z_pm25 > 2.0
        is_co2_elevated = co2 > 950.0 or z_co2 > 2.0
        is_voc_elevated = voc > 280.0 or z_voc > 2.0

        # Calculate composite anomaly score (0.0 to 100.0)
        anomaly_score = min(100.0, (z_pm25 * 14.0 + z_co2 * 12.0 + z_voc * 12.0))
        is_anomaly = anomaly_score >= 35.0 or is_pm_elevated or is_co2_elevated or is_voc_elevated

        # Severity determination
        if anomaly_score < 25.0:
            severity = "NORMAL"
        elif anomaly_score < 45.0:
            severity = "LOW"
        elif anomaly_score < 70.0:
            severity = "MEDIUM"
        elif anomaly_score < 90.0:
            severity = "HIGH"
        else:
            severity = "CRITICAL"

        # Multi-sensor cross-correlation root-cause classification
        root_cause_code, root_cause_title, description, recommendation = self._classify_root_cause(
            pm25=pm25,
            co2=co2,
            voc=voc,
            temp=temp,
            humidity=humidity,
            is_pm_elevated=is_pm_elevated,
            is_co2_elevated=is_co2_elevated,
            is_voc_elevated=is_voc_elevated,
            z_pm25=z_pm25,
            z_co2=z_co2,
            z_voc=z_voc
        )

        sensor_contributions = {
            "PM2.5": round(min(100.0, z_pm25 * 25.0), 1),
            "CO2": round(min(100.0, z_co2 * 25.0), 1),
            "VOC": round(min(100.0, z_voc * 25.0), 1)
        }

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": round(anomaly_score, 1),
            "severity": severity,
            "root_cause_code": root_cause_code,
            "root_cause_title": root_cause_title,
            "description": description,
            "recommendation": recommendation,
            "sensor_contributions": sensor_contributions,
            "metrics": {
                "pm2_5": pm25,
                "co2": co2,
                "voc": voc,
                "temperature": temp,
                "humidity": humidity,
                "z_pm2_5": round(z_pm25, 2),
                "z_co2": round(z_co2, 2),
                "z_voc": round(z_voc, 2)
            }
        }

    def _calculate_baselines(self, historical_readings: Optional[List[Dict[str, float]]]) -> Dict[str, Dict[str, float]]:
        if not historical_readings or len(historical_readings) < 10:
            return self.default_baselines

        baselines = {}
        for key in ["pm2_5", "pm10", "co2", "voc", "temperature", "humidity"]:
            values = [float(r[key]) for r in historical_readings if key in r and r[key] is not None]
            if len(values) >= 5:
                arr = np.array(values)
                med = float(np.median(arr))
                std = float(np.std(arr)) if float(np.std(arr)) > 0 else 1.0
                p95 = float(np.percentile(arr, 95))
                baselines[key] = {"median": med, "std": std, "p95": p95}
            else:
                baselines[key] = self.default_baselines.get(key, {"median": 10.0, "std": 5.0, "p95": 20.0})
        return baselines

    def _classify_root_cause(
        self,
        pm25: float,
        co2: float,
        voc: float,
        temp: float,
        humidity: float,
        is_pm_elevated: bool,
        is_co2_elevated: bool,
        is_voc_elevated: bool,
        z_pm25: float,
        z_co2: float,
        z_voc: float
    ):
        """
        Cross-correlates combinations of sensor deviations to accurately pinpoint the source.
        """
        if not (is_pm_elevated or is_co2_elevated or is_voc_elevated):
            return (
                "CLEAN_STABLE",
                "Atmosphere Optimal & Nominal",
                "All environmental sensors are within safe baseline limits. No pollution sources detected.",
                "Maintain normal room use; no action required."
            )

        # Case 1: High PM2.5 and High VOC (isolated or dominant) -> Cooking / Frying / Culinary Smoke
        if is_pm_elevated and is_voc_elevated and (z_pm25 > 2.0 or pm25 > 35.0):
            return (
                "COOKING_SMOKE",
                "Culinary Activities / Frying Smoke",
                f"Simultaneous surge in fine particulates (PM2.5: {pm25} µg/m³) and volatile organic vapors (VOC: {voc} ppb) strongly indicates frying, boiling oil, or high-heat cooking emissions.",
                "Turn on kitchen exhaust range hood immediately and close interior room doors to prevent particulate spread."
            )

        # Case 2: High CO2 and High VOC, normal/low PM2.5 -> Poor Ventilation / High Occupancy
        if is_co2_elevated and is_voc_elevated and not is_pm_elevated:
            return (
                "POOR_VENTILATION_OCCUPANCY",
                "Inadequate Ventilation / High Occupancy",
                f"Elevated CO2 ({int(co2)} ppm) alongside human metabolic VOC build-up ({voc} ppb) with clean particulate levels indicates prolonged closed-door occupancy without fresh air exchange.",
                "Open windows across the room to create cross-ventilation, or increase HVAC fresh air intake damper."
            )

        # Case 3: High VOC spike alone, normal CO2 and normal PM2.5 -> Chemical cleaner / Solvents / Paint
        if is_voc_elevated and not is_pm_elevated and not is_co2_elevated:
            return (
                "CHEMICAL_SOLVENT_EVAPORATION",
                "Chemical Cleaners / Aerosol / Solvent Off-gassing",
                f"Sharp spike in VOC ({voc} ppb) with baseline CO2 and PM2.5 confirms gaseous off-gassing from cleaning agents, perfumes, paints, or alcohol-based disinfectants.",
                "Identify and seal active chemical containers; open windows to purge chemical vapors."
            )

        # Case 4: High PM2.5 alone, normal VOC and normal CO2 -> Outdoor Wildfire / Dust / Vacuuming
        if is_pm_elevated and not is_voc_elevated and not is_co2_elevated:
            return (
                "PARTICULATE_INFILTRATION",
                "Outdoor Infiltration / Dust / Wildfire Smoke",
                f"Isolated particulate spike (PM2.5: {pm25} µg/m³) without VOC or CO2 rise suggests outdoor smog entering via leaky seals, dust re-suspension, or vacuuming without HEPA filtration.",
                "Keep windows tightly closed and activate standalone HEPA air purifier on high speed."
            )

        # Case 5: High CO2 alone -> Stagnant Closed Room / Exhalation
        if is_co2_elevated and not is_pm_elevated and not is_voc_elevated:
            return (
                "CLOSED_ROOM_STAGNATION",
                "Room Air Stagnation / Metabolic CO₂ Accumulation",
                f"Carbon dioxide has reached {int(co2)} ppm due to natural respiration in an unventilated enclosed space, causing cognitive fatigue and drowsiness.",
                "Crack open the door or window for 10-15 minutes to restore fresh oxygen and drop CO2 below 800 ppm."
            )

        # Case 6: All sensors elevated -> Severe Multi-Source Event
        if is_pm_elevated and is_co2_elevated and is_voc_elevated:
            return (
                "CRITICAL_POLLUTION_ACCUMULATION",
                "Compound Indoor Pollution Build-up",
                f"PM2.5 ({pm25} µg/m³), CO2 ({int(co2)} ppm), and VOC ({voc} ppb) are all concurrently exceeding health guidelines, indicating high indoor activity in a sealed environment.",
                "Emergency ventilation required: Open all windows, activate range hood and air purifiers immediately."
            )

        # Fallback general elevation
        return (
            "GENERAL_ATMOSPHERIC_DEVIATION",
            "General Atmospheric Anomaly",
            "One or more environmental indicators have deviated from historical baseline medians.",
            "Inspect the room for ongoing combustion, candles, or blocked air returns."
        )


anomaly_engine = AnomalyEngine()
