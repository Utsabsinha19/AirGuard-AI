"""
AirGuard AI - Multi-Sensor Context-Aware Anomaly Detection & Diagnostic Engine (FR-4.3, Section 2.2)
Enhanced with:
- Barometric weather inversion and pressure drop correlations
- Acoustic noise and human activity occupancy correlations
- Circadian ambient light correlations (distinguishing daytime culinary smoke vs nighttime smoldering/candles)
- Unoccupied silent chemical off-gassing leaks
"""

from typing import Dict, Any, List, Optional
import numpy as np


class AnomalyEngine:
    def __init__(self):
        self.default_baselines = {
            "pm2_5": {"median": 10.0, "std": 5.0, "p95": 25.0},
            "pm10": {"median": 18.0, "std": 8.0, "p95": 40.0},
            "co2": {"median": 650.0, "std": 120.0, "p95": 950.0},
            "voc": {"median": 120.0, "std": 45.0, "p95": 250.0},
            "temperature": {"median": 22.0, "std": 2.0, "p95": 26.0},
            "humidity": {"median": 45.0, "std": 8.0, "p95": 65.0},
            "pressure": {"median": 1013.25, "std": 4.0, "p95": 1020.0},
            "noise_level": {"median": 40.0, "std": 8.0, "p95": 65.0},
            "ambient_light": {"median": 150.0, "std": 100.0, "p95": 450.0}
        }

    def detect_anomalies_and_diagnose(
        self,
        current_reading: Dict[str, float],
        historical_readings: Optional[List[Dict[str, float]]] = None
    ) -> Dict[str, Any]:
        baselines = self._calculate_baselines(historical_readings)

        pm25 = float(current_reading.get("pm2_5", 0.0) or 0.0)
        pm10 = float(current_reading.get("pm10", pm25 * 1.4) or 0.0)
        co2 = float(current_reading.get("co2", 600.0) or 600.0)
        voc = float(current_reading.get("voc", 100.0) or 100.0)
        temp = float(current_reading.get("temperature", 22.0) or 22.0)
        humidity = float(current_reading.get("humidity", 45.0) or 45.0)
        pressure = float(current_reading.get("pressure", 1013.25) or 1013.25)
        noise = float(current_reading.get("noise_level", 42.0) or 42.0)
        light = float(current_reading.get("ambient_light", 150.0) or 150.0)

        # Standard z-scores relative to baseline
        z_pm25 = max(0.0, (pm25 - baselines["pm2_5"]["median"]) / max(1.0, baselines["pm2_5"]["std"]))
        z_co2 = max(0.0, (co2 - baselines["co2"]["median"]) / max(1.0, baselines["co2"]["std"]))
        z_voc = max(0.0, (voc - baselines["voc"]["median"]) / max(1.0, baselines["voc"]["std"]))
        z_noise = max(0.0, (noise - baselines["noise_level"]["median"]) / max(1.0, baselines["noise_level"]["std"]))

        is_pm_elevated = pm25 > 25.0 or z_pm25 > 2.0
        is_co2_elevated = co2 > 950.0 or z_co2 > 2.0
        is_voc_elevated = voc > 280.0 or z_voc > 2.0
        is_noise_elevated = noise > 60.0 or z_noise > 2.0
        is_barometric_drop = pressure < 1006.0

        # Composite anomaly score (0.0 to 100.0)
        anomaly_score = min(100.0, (z_pm25 * 14.0 + z_co2 * 12.0 + z_voc * 12.0 + (z_noise * 4.0 if is_noise_elevated else 0.0)))
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

        # Context-aware root-cause classification
        root_cause_code, root_cause_title, description, recommendation = self._classify_root_cause(
            pm25=pm25,
            co2=co2,
            voc=voc,
            temp=temp,
            humidity=humidity,
            pressure=pressure,
            noise=noise,
            light=light,
            is_pm_elevated=is_pm_elevated,
            is_co2_elevated=is_co2_elevated,
            is_voc_elevated=is_voc_elevated,
            is_noise_elevated=is_noise_elevated,
            is_barometric_drop=is_barometric_drop,
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
                "pressure": pressure,
                "noise_level": noise,
                "ambient_light": light,
                "z_pm2_5": round(z_pm25, 2),
                "z_co2": round(z_co2, 2),
                "z_voc": round(z_voc, 2)
            }
        }

    def _calculate_baselines(self, historical_readings: Optional[List[Dict[str, float]]]) -> Dict[str, Dict[str, float]]:
        if not historical_readings or len(historical_readings) < 10:
            return self.default_baselines

        baselines = {}
        for key in ["pm2_5", "pm10", "co2", "voc", "temperature", "humidity", "pressure", "noise_level", "ambient_light"]:
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
        pressure: float,
        noise: float,
        light: float,
        is_pm_elevated: bool,
        is_co2_elevated: bool,
        is_voc_elevated: bool,
        is_noise_elevated: bool,
        is_barometric_drop: bool,
        z_pm25: float,
        z_co2: float,
        z_voc: float
    ):
        if not (is_pm_elevated or is_co2_elevated or is_voc_elevated):
            return (
                "CLEAN_STABLE",
                "Atmosphere Optimal & Nominal",
                "All environmental sensors are within safe baseline limits. No pollution sources detected.",
                "Maintain normal room use; no action required."
            )

        # Context Case A: Nighttime Smoldering Combustion (Light < 15 lux, high PM2.5)
        if is_pm_elevated and light < 15.0 and (z_pm25 > 2.0 or pm25 > 30.0):
            return (
                "NIGHTTIME_SMOLDERING",
                "Nighttime Smoldering / Candle / Unattended Combustion",
                f"Particulate surge (PM2.5: {pm25} µg/m³) detected in darkness ({int(light)} lux) indicates burning candles, incense, or unattended smoldering materials.",
                "Inspect the room immediately for burning wicks, candles, or electrical overheating."
            )

        # Context Case B: High Occupancy Gathering (Elevated Noise + CO2 + VOC)
        if is_co2_elevated and is_voc_elevated and is_noise_elevated:
            return (
                "HIGH_OCCUPANCY_ACTIVITY",
                "High Room Occupancy & Social Gathering",
                f"Concurrent elevation in CO2 ({int(co2)} ppm), metabolic VOC ({voc} ppb), and acoustic noise ({int(noise)} dB) confirms high human occupancy and physical activity.",
                "Open multiple doors and windows to cross-ventilate and purge accumulated exhaled air."
            )

        # Context Case C: Weather Inversion / Frontal Storm Pressure Drop
        if is_pm_elevated and is_barometric_drop and not is_voc_elevated:
            return (
                "WEATHER_INVERSION_SMOG",
                "Weather Inversion & Outdoor Smog Trapping",
                f"Falling barometric pressure ({pressure} hPa) combined with fine particulates ({pm25} µg/m³) indicates a regional inversion layer trapping outdoor particulates indoors.",
                "Keep windows tightly sealed and run standalone HEPA filtration continuously."
            )

        # Standard Case 1: High PM2.5 and High VOC -> Cooking / Culinary smoke
        if is_pm_elevated and is_voc_elevated and (z_pm25 > 2.0 or pm25 > 35.0):
            return (
                "COOKING_SMOKE",
                "Culinary Activities / Frying Smoke",
                f"Simultaneous surge in fine particulates (PM2.5: {pm25} µg/m³) and volatile organic vapors (VOC: {voc} ppb) strongly indicates frying, boiling oil, or high-heat cooking emissions.",
                "Turn on kitchen exhaust range hood immediately and close interior room doors."
            )

        # Standard Case 2: High CO2 + High VOC (Normal PM) -> Poor Ventilation
        if is_co2_elevated and is_voc_elevated and not is_pm_elevated:
            return (
                "POOR_VENTILATION_OCCUPANCY",
                "Inadequate Ventilation / High Occupancy",
                f"Elevated CO2 ({int(co2)} ppm) alongside human metabolic VOC build-up ({voc} ppb) with clean particulate levels indicates prolonged closed-door occupancy.",
                "Open windows across the room to create cross-ventilation, or increase HVAC fresh air intake damper."
            )

        # Standard Case 3: High VOC alone -> Chemical Solvent / Unoccupied Off-Gassing
        if is_voc_elevated and not is_pm_elevated and not is_co2_elevated:
            unocc_text = " (Silent room indicates unattended off-gassing container)" if noise < 42.0 else ""
            return (
                "CHEMICAL_SOLVENT_EVAPORATION",
                "Chemical Cleaners / Aerosol / Solvent Off-gassing",
                f"Sharp spike in VOC ({voc} ppb) with baseline CO2 and PM2.5 confirms gaseous off-gassing from cleaning agents, paints, or disinfectants.{unocc_text}",
                "Identify and seal active chemical containers; open windows to purge chemical vapors."
            )

        # Standard Case 4: High PM2.5 alone -> Outdoor Infiltration / Dust
        if is_pm_elevated and not is_voc_elevated and not is_co2_elevated:
            return (
                "PARTICULATE_INFILTRATION",
                "Outdoor Infiltration / Dust / Wildfire Smoke",
                f"Isolated particulate spike (PM2.5: {pm25} µg/m³) without VOC or CO2 rise suggests outdoor smog entering via leaky seals or vacuuming without HEPA filtration.",
                "Keep windows tightly closed and activate standalone HEPA air purifier on high speed."
            )

        # Standard Case 5: High CO2 alone -> Closed Room Stagnation
        if is_co2_elevated and not is_pm_elevated and not is_voc_elevated:
            return (
                "CLOSED_ROOM_STAGNATION",
                "Room Air Stagnation / Metabolic CO₂ Accumulation",
                f"Carbon dioxide has reached {int(co2)} ppm due to natural respiration in an unventilated enclosed space.",
                "Crack open the door or window for 10-15 minutes to restore fresh oxygen."
            )

        return (
            "GENERAL_ATMOSPHERIC_DEVIATION",
            "General Atmospheric Anomaly",
            "One or more environmental indicators have deviated from historical baseline medians.",
            "Inspect the room for ongoing combustion, candles, or blocked air returns."
        )


anomaly_engine = AnomalyEngine()
