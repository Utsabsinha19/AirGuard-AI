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
        hcho = float(current_reading.get("hcho", 0.0) or 0.0)
        outdoor_pm25 = float(current_reading.get("outdoor_pm25", 0.0) or 0.0)
        flow_rate = float(current_reading.get("flow_rate", 100.0) or 100.0)

        # Standard z-scores relative to baseline
        z_pm25 = max(0.0, (pm25 - baselines["pm2_5"]["median"]) / max(1.0, baselines["pm2_5"]["std"]))
        z_co2 = max(0.0, (co2 - baselines["co2"]["median"]) / max(1.0, baselines["co2"]["std"]))
        z_voc = max(0.0, (voc - baselines["voc"]["median"]) / max(1.0, baselines["voc"]["std"]))
        z_noise = max(0.0, (noise - baselines["noise_level"]["median"]) / max(1.0, baselines["noise_level"]["std"]))

        is_pm_elevated = pm25 > 25.0 or (pm25 > 15.0 and z_pm25 > 2.0)
        is_co2_elevated = co2 > 950.0 or (co2 > 800.0 and z_co2 > 2.0)
        is_voc_elevated = voc > 280.0 or (voc > 200.0 and z_voc > 2.0)
        is_hcho_elevated = hcho > 0.08
        is_noise_elevated = noise > 60.0 or (noise > 50.0 and z_noise > 2.0)
        is_barometric_drop = pressure < 1006.0

        # Composite anomaly score (0.0 to 100.0)
        anomaly_score = min(100.0, (z_pm25 * 14.0 + z_co2 * 12.0 + z_voc * 12.0 + (z_noise * 4.0 if is_noise_elevated else 0.0) + (35.0 if is_hcho_elevated else 0.0)))
        is_anomaly = anomaly_score >= 35.0 or is_pm_elevated or is_co2_elevated or is_voc_elevated or is_hcho_elevated

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

        # Context-aware root-cause classification (v2.0 & v3.0 Multi-Sensor Matrix)
        root_cause_code, root_cause_title, description, recommendation = self._classify_root_cause(
            pm25=pm25,
            pm10=pm10,
            co2=co2,
            voc=voc,
            temp=temp,
            humidity=humidity,
            pressure=pressure,
            noise=noise,
            light=light,
            hcho=hcho,
            outdoor_pm25=outdoor_pm25,
            flow_rate=flow_rate,
            is_pm_elevated=is_pm_elevated,
            is_co2_elevated=is_co2_elevated,
            is_voc_elevated=is_voc_elevated,
            is_hcho_elevated=is_hcho_elevated,
            is_noise_elevated=is_noise_elevated,
            is_barometric_drop=is_barometric_drop,
            z_pm25=z_pm25,
            z_co2=z_co2,
            z_voc=z_voc
        )

        sensor_contributions = {
            "PM2.5": round(min(100.0, z_pm25 * 25.0), 1),
            "CO2": round(min(100.0, z_co2 * 25.0), 1),
            "VOC": round(min(100.0, z_voc * 25.0), 1),
            "HCHO": round(min(100.0, (hcho / 0.08) * 50.0), 1) if hcho > 0 else 0.0
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
                "pm10": pm10,
                "co2": co2,
                "voc": voc,
                "temperature": temp,
                "humidity": humidity,
                "pressure": pressure,
                "ambient_light": light,
                "noise_level": noise,
                "hcho": hcho,
                "z_pm2_5": round(z_pm25, 2),
                "z_co2": round(z_co2, 2),
                "z_voc": round(z_voc, 2)
            }
        }

    def _calculate_baselines(self, historical_readings: Optional[List[Dict[str, float]]]) -> Dict[str, Dict[str, float]]:
        if not historical_readings or len(historical_readings) < 10:
            return self.default_baselines

        baselines = {}
        for key in ["pm2_5", "pm10", "co2", "voc", "temperature", "humidity", "pressure", "noise_level", "ambient_light", "hcho"]:
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
        pm10: float,
        co2: float,
        voc: float,
        temp: float,
        humidity: float,
        pressure: float,
        noise: float,
        light: float,
        hcho: float,
        outdoor_pm25: float,
        flow_rate: float,
        is_pm_elevated: bool,
        is_co2_elevated: bool,
        is_voc_elevated: bool,
        is_hcho_elevated: bool,
        is_noise_elevated: bool,
        is_barometric_drop: bool,
        z_pm25: float,
        z_co2: float,
        z_voc: float
    ):
        if not (is_pm_elevated or is_co2_elevated or is_voc_elevated or is_hcho_elevated):
            return (
                "CLEAN_STABLE",
                "Atmosphere Optimal & Nominal",
                "All environmental sensors are within safe baseline limits. No pollution sources detected.",
                "Maintain normal room use; no action required."
            )

        # v3.0 Incident: Material Off-Gassing (HCHO > 0.08 ppm + VOC, Normal CO2 & PM2.5)
        if (is_hcho_elevated or hcho > 0.08) and (not is_pm_elevated and not is_co2_elevated):
            return (
                "MATERIAL_OFF_GASSING",
                "Chemical Off-gassing (New Furniture/Paint)",
                f"Elevated Formaldehyde ({hcho:.3f} ppm) and volatile organic vapors ({voc} ppb) detected with normal CO2 and PM2.5 confirms chemical off-gassing from new furniture, carpeting, or building materials.",
                "Trigger Continuous Mechanical Ventilation"
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

        # v3.0 Incident: Wildfire Smoke Infiltration (PM2.5 >= 75 or outdoor_pm25 > 30, with PM10 surge or pressure drop)
        if (pm25 >= 75.0 or outdoor_pm25 > 30.0) and pm10 > 45.0 and (outdoor_pm25 > 30.0 or is_barometric_drop or pm25 > 90.0):
            return (
                "WILDFIRE_SMOKE_INFILTRATION",
                "Outdoor Smoke Infiltration",
                f"Elevated indoor PM2.5 ({pm25} µg/m³) and PM10 ({pm10} µg/m³) coinciding with outdoor wildfire pollution ({outdoor_pm25} µg/m³) or atmospheric pressure drop confirms building envelope infiltration.",
                "Seal Windows, Set HVAC to Recirculation, Max HEPA"
            )

        # Context Case C: Weather Inversion / Frontal Storm Pressure Drop
        if is_pm_elevated and is_barometric_drop and not is_voc_elevated:
            return (
                "WEATHER_INVERSION_SMOG",
                "Weather Inversion & Outdoor Smog Trapping",
                f"Falling barometric pressure ({pressure} hPa) combined with fine particulates ({pm25} µg/m³) indicates a regional inversion layer trapping outdoor particulates indoors.",
                "Keep windows tightly sealed and run standalone HEPA filtration continuously."
            )

        # v2.0 / v3.0 Signature 1: Indoor Combustion (Sudden PM2.5 > 50 or elevated + VOC, Stable CO2)
        if is_pm_elevated and is_voc_elevated and (z_pm25 > 2.0 or pm25 > 35.0):
            return (
                "COOKING_SMOKE",
                "Indoor Cooking, Frying, or Smoke Event",
                f"Sudden surge in fine particulates (PM2.5: {pm25} µg/m³) and volatile vapors (VOC: {voc} ppb) with stable CO2 indicates indoor cooking, frying, or smoke emissions.",
                "Activate Kitchen Exhaust & Max Air Purifier Speed"
            )

        # v2.0 / v3.0 Signature 2: Occupancy Stagnation (Rapid CO2 > 1200 + VOC, Stable PM2.5)
        if is_co2_elevated and is_voc_elevated and not is_pm_elevated:
            return (
                "POOR_VENTILATION_OCCUPANCY",
                "Poor Indoor Ventilation / High Room Occupancy",
                f"Elevated CO2 ({int(co2)} ppm) alongside metabolic VOC accumulation ({voc} ppb) with stable particulate levels indicates inadequate ventilation.",
                "Open Automated Smart Windows or HVAC Damper"
            )

        # v3.0 Signature 5: HVAC Filter Saturation / Flow Rate Reduction
        if (is_pm_elevated or pm25 > 20.0) and flow_rate < 75.0 and not is_voc_elevated and not is_co2_elevated:
            return (
                "HVAC_FILTER_FAILURE",
                "Filter Efficiency Degradation",
                f"Persistent particulate baseline shift (PM2.5: {pm25} µg/m³) with reduced air handler flow rate ({flow_rate}%) indicates saturated filtration media.",
                "Dispatch Replacement Filter Alert to Mobile App"
            )

        # v2.0 Signature 3: HVAC / Filter Failure (Gradual PM2.5 + PM10 + Humidity, Stable CO2/VOC)
        if (is_pm_elevated or pm25 > 20.0) and (pm10 > 25.0) and humidity > 52.0 and not is_voc_elevated and not is_co2_elevated:
            return (
                "HVAC_FILTER_FAILURE",
                "HVAC Filter Saturation or Outdoor Infiltration",
                f"Gradual rise in PM2.5 ({pm25} µg/m³) and PM10 ({pm10} µg/m³) accompanied by humidity ({humidity}%) indicates saturated HVAC filtration or envelope leakage.",
                "Inspect and clean air purifier / HVAC filters"
            )

        # v2.0 Signature 4: Volatile Chemical Event (Spike in VOCs, Normal CO2 & PM2.5)
        if is_voc_elevated and not is_pm_elevated and not is_co2_elevated:
            unocc_text = " (Silent room indicates unattended off-gassing container)" if noise < 42.0 else ""
            return (
                "CHEMICAL_SOLVENT_EVAPORATION",
                "Household Cleaning Chemical or Solvent Use",
                f"Sharp spike in VOCs ({voc} ppb) with normal CO2 and PM2.5 confirms household chemical cleaner, solvent, or paint off-gassing.{unocc_text}",
                "Increase air circulation and avoid enclosed exposure"
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
