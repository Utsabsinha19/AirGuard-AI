"""
AirGuard AI - Sensor Calibration & Standard AQI Computation Module (FR-4.4, Section 2.2)
Implements:
1. Non-linear optical hygroscopic growth correction for PM2.5 (PMS5003).
2. Temperature and humidity cross-calibration / baseline drift for metal-oxide VOC (SGP30).
3. Device-specific dynamic zero-point baseline auto-calibration and gain compensation.
4. US EPA Standard AQI computation with piecewise linear interpolation.
"""

import math
from typing import Dict, Any, Tuple


def calculate_absolute_humidity(temp_c: float, humidity_rh: float) -> float:
    if temp_c is None or humidity_rh is None:
        return 10.0
    svp = 6.112 * math.exp((17.62 * temp_c) / (243.12 + temp_c))
    vp = (humidity_rh / 100.0) * svp
    ah = 216.7 * (vp / (273.15 + temp_c))
    return max(0.1, ah)


def calibrate_pm25(
    raw_pm25: float,
    humidity_rh: float,
    temp_c: float = 22.0,
    zero_offset: float = 0.0,
    gain_scale: float = 1.0,
    a: float = 0.38,
    b: float = 2.5
) -> float:
    """
    Corrects optical PM2.5 hygroscopic aerosol swelling (v2.0 Section 2.3):
    PM2.5_calibrated = PM2.5_raw / (1 + a * (RH / 100)^b)
    Also applies device-specific zero offset and sensitivity gain factor.
    """
    if raw_pm25 is None or raw_pm25 < 0:
        return 0.0

    # Adjust for device zero offset and gain
    adjusted_raw = max(0.0, (raw_pm25 - zero_offset) * gain_scale)

    if humidity_rh is None:
        return round(float(adjusted_raw), 1)

    rh = max(0.0, min(99.0, float(humidity_rh)))
    if rh <= 40.0:
        return round(float(adjusted_raw), 1)

    correction_factor = 1.0 + a * ((rh / 100.0) ** b)
    calibrated = adjusted_raw / correction_factor
    return round(max(0.0, calibrated), 1)


def calibrate_voc(
    raw_voc_ppb: float,
    temp_c: float,
    humidity_rh: float,
    zero_offset: float = 0.0,
    gain_scale: float = 1.0
) -> float:
    """
    Compensates Sensirion SGP30 MOX sensor for absolute humidity and thermal drift.
    Also applies baseline calibration offset.
    """
    if raw_voc_ppb is None or raw_voc_ppb < 0:
        return 0.0

    adjusted_raw = max(0.0, (raw_voc_ppb - zero_offset) * gain_scale)

    temp = 22.0 if temp_c is None else float(temp_c)
    rh = 50.0 if humidity_rh is None else float(humidity_rh)

    target_ah = 11.5
    current_ah = calculate_absolute_humidity(temp, rh)
    compensation = 1.0 + 0.012 * (target_ah - current_ah)
    calibrated = adjusted_raw * compensation
    return round(max(0.0, calibrated), 1)


# US EPA AQI Breakpoints
PM25_BREAKPOINTS = [
    (0.0, 12.0, 0, 50),
    (12.1, 35.4, 51, 100),
    (35.5, 55.4, 101, 150),
    (55.5, 150.4, 151, 200),
    (150.5, 250.4, 201, 300),
    (250.5, 500.4, 301, 500)
]

PM10_BREAKPOINTS = [
    (0, 54, 0, 50),
    (55, 154, 51, 100),
    (155, 254, 101, 150),
    (255, 354, 151, 200),
    (355, 424, 201, 300),
    (425, 604, 301, 500)
]

CO2_BREAKPOINTS = [
    (400, 700, 0, 50),
    (701, 1000, 51, 100),
    (1001, 1500, 101, 150),
    (1501, 2000, 151, 200),
    (2001, 3000, 201, 300),
    (3001, 5000, 301, 500)
]

VOC_BREAKPOINTS = [
    (0, 150, 0, 50),
    (151, 300, 51, 100),
    (301, 500, 101, 150),
    (501, 1000, 151, 200),
    (1001, 2000, 201, 300),
    (2001, 5000, 301, 500)
]


def _interpolate_aqi(val: float, breakpoints: list) -> int:
    if val is None or val < 0:
        return 0
    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= val <= c_high:
            aqi = ((i_high - i_low) / (c_high - c_low)) * (val - c_low) + i_low
            return int(round(aqi))
    if val > breakpoints[-1][1]:
        return 500
    return 0


def get_aqi_category(aqi: int) -> Tuple[str, str, str]:
    if aqi <= 50:
        return ("Good", "#10b981", "Air quality is ideal. Enjoy normal indoor and outdoor activities.")
    elif aqi <= 100:
        return ("Moderate", "#eab308", "Air quality is acceptable. Sensitive individuals should monitor symptoms.")
    elif aqi <= 150:
        return ("Unhealthy for Sensitive Groups", "#f97316", "Members of sensitive groups may experience health effects.")
    elif aqi <= 200:
        return ("Unhealthy", "#ef4444", "Everyone may begin to experience health effects. Increase ventilation.")
    elif aqi <= 300:
        return ("Very Unhealthy", "#a855f7", "Health alert: risk of health effects increased for all occupants.")
    else:
        return ("Hazardous", "#881337", "Emergency conditions: serious risk of respiratory impact.")


def compute_comprehensive_aqi(
    pm25: float,
    pm10: float = None,
    co2: float = None,
    voc: float = None
) -> Dict[str, Any]:
    sub_indices = {}
    if pm25 is not None:
        sub_indices["PM2.5"] = _interpolate_aqi(pm25, PM25_BREAKPOINTS)
    if pm10 is not None:
        sub_indices["PM10"] = _interpolate_aqi(pm10, PM10_BREAKPOINTS)
    if co2 is not None:
        sub_indices["CO2"] = _interpolate_aqi(co2, CO2_BREAKPOINTS)
    if voc is not None:
        sub_indices["VOC"] = _interpolate_aqi(voc, VOC_BREAKPOINTS)

    if not sub_indices:
        overall_aqi = 0
        dominant_pollutant = "None"
    else:
        dominant_pollutant = max(sub_indices, key=sub_indices.get)
        overall_aqi = sub_indices[dominant_pollutant]

    overall_aqi = min(500, max(0, overall_aqi))
    category, color, advice = get_aqi_category(overall_aqi)

    return {
        "aqi": overall_aqi,
        "category": category,
        "color": color,
        "dominant_pollutant": dominant_pollutant,
        "health_advice": advice,
        "sub_indices": sub_indices
    }
