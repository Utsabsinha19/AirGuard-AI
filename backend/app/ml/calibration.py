"""
AirGuard AI - Sensor Calibration & Standard AQI Computation Module
Implements:
1. Non-linear optical hygroscopic growth correction for PM2.5 (PMS5003).
2. Temperature and humidity cross-calibration / baseline drift for metal-oxide VOC (SGP30).
3. US EPA Standard AQI computation with piecewise linear interpolation.
"""

import math
from typing import Dict, Any, Tuple


def calculate_absolute_humidity(temp_c: float, humidity_rh: float) -> float:
    """
    Computes absolute humidity in g/m^3 based on temperature (Celsius)
    and relative humidity (%).
    """
    if temp_c is None or humidity_rh is None:
        return 10.0
    # Saturation vapor pressure in hPa
    svp = 6.112 * math.exp((17.62 * temp_c) / (243.12 + temp_c))
    # Actual vapor pressure
    vp = (humidity_rh / 100.0) * svp
    # Absolute humidity in g/m^3
    ah = 216.7 * (vp / (273.15 + temp_c))
    return max(0.1, ah)


def calibrate_pm25(raw_pm25: float, humidity_rh: float, temp_c: float = 22.0) -> float:
    """
    Corrects optical PM2.5 hygroscopic swelling error.
    Laser particle counters (like PMS5003) overestimate particulate mass
    at high relative humidity (RH > 50%) due to hygroscopic aerosol growth.
    Applies empirical polynomial kappa-Kohler correction:
    CF = 1 + alpha * (RH / (100 - RH))^beta for RH > 50%
    """
    if raw_pm25 is None or raw_pm25 < 0:
        return 0.0
    if humidity_rh is None:
        return float(raw_pm25)

    # Clamping humidity to physical range
    rh = max(0.0, min(99.0, float(humidity_rh)))

    if rh <= 50.0:
        # Minimal hygroscopic growth below 50% RH
        return round(float(raw_pm25), 1)

    # Hygroscopic expansion factor
    # For RH between 50% and 99%
    rh_norm = (rh - 50.0) / 50.0
    correction_factor = 1.0 + 0.35 * (rh_norm ** 2.0)
    
    calibrated = raw_pm25 / correction_factor
    return round(max(0.0, calibrated), 1)


def calibrate_voc(raw_voc_ppb: float, temp_c: float, humidity_rh: float) -> float:
    """
    Compensates metal-oxide (MOX) VOC sensor (SGP30) for temperature and humidity drift.
    Sensirion SGP30 baseline resistance shifts with absolute water vapor.
    """
    if raw_voc_ppb is None or raw_voc_ppb < 0:
        return 0.0
    
    temp = 22.0 if temp_c is None else float(temp_c)
    rh = 50.0 if humidity_rh is None else float(humidity_rh)

    # Baseline condition: 25°C, 50% RH -> AH approx 11.5 g/m^3
    target_ah = 11.5
    current_ah = calculate_absolute_humidity(temp, rh)

    # Empirical sensitivity compensation: 1.2% shift per g/m^3 deviation
    compensation = 1.0 + 0.012 * (target_ah - current_ah)
    calibrated = raw_voc_ppb * compensation
    return round(max(0.0, calibrated), 1)


# US EPA AQI Breakpoints (Concentration Breakpoints in ug/m3 for PM2.5 and PM10)
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

# Indoor CO2 Sub-index Breakpoints (ppm)
CO2_BREAKPOINTS = [
    (400, 700, 0, 50),        # Fresh outdoor air equivalent
    (701, 1000, 51, 100),     # Acceptable indoor air
    (1001, 1500, 101, 150),   # Drowsiness, poor air exchange
    (1501, 2000, 151, 200),   # Headaches, lethargy, poor ventilation
    (2001, 3000, 201, 300),   # Significant cognitive impairment
    (3001, 5000, 301, 500)    # Hazardous occupational threshold
]

# VOC Sub-index Breakpoints (ppb)
VOC_BREAKPOINTS = [
    (0, 150, 0, 50),          # Clean indoor air
    (151, 300, 51, 100),      # Normal indoor level
    (301, 500, 101, 150),     # Elevated VOC, potential irritation
    (501, 1000, 151, 200),    # Unhealthy chemical load
    (1001, 2000, 201, 300),   # High solvent/chemical exposure
    (2001, 5000, 301, 500)    # Hazardous VOC level
]


def _interpolate_aqi(val: float, breakpoints: list) -> int:
    """Calculates linear piece-wise sub-index."""
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
    """
    Returns (category_name, hex_color, health_advisory).
    """
    if aqi <= 50:
        return (
            "Good",
            "#10b981",  # Emerald Green
            "Air quality is ideal. Enjoy normal indoor and outdoor activities."
        )
    elif aqi <= 100:
        return (
            "Moderate",
            "#eab308",  # Amber / Yellow
            "Air quality is acceptable. Unusually sensitive individuals should monitor symptoms."
        )
    elif aqi <= 150:
        return (
            "Unhealthy for Sensitive Groups",
            "#f97316",  # Orange
            "Members of sensitive groups may experience health effects. General public not likely affected."
        )
    elif aqi <= 200:
        return (
            "Unhealthy",
            "#ef4444",  # Red
            "Everyone may begin to experience health effects. Activate air purifiers or increase ventilation."
        )
    elif aqi <= 300:
        return (
            "Very Unhealthy",
            "#a855f7",  # Purple
            "Health alert: risk of health effects increased for everyone. Avoid indoor physical exertion."
        )
    else:
        return (
            "Hazardous",
            "#881337",  # Maroon
            "Emergency conditions: serious risk of respiratory impact. Take immediate remediation."
        )


def compute_comprehensive_aqi(
    pm25: float,
    pm10: float = None,
    co2: float = None,
    voc: float = None
) -> Dict[str, Any]:
    """
    Computes overall composite AQI as the maximum of individual pollutant sub-indices,
    identifying the dominant pollutant and status category.
    """
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
