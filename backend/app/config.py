"""
AirGuard AI - Application Configuration & Threshold Settings
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "AirGuard AI"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./airguard.db")
    
    # MQTT Broker Settings
    MQTT_BROKER_HOST: str = os.getenv("MQTT_BROKER_HOST", "localhost")
    MQTT_BROKER_PORT: int = int(os.getenv("MQTT_BROKER_PORT", "1883"))
    MQTT_TELEMETRY_TOPIC: str = "airguard/+/telemetry"
    MQTT_COMMAND_TOPIC: str = "airguard/{device_id}/command"
    MQTT_USERNAME: str = os.getenv("MQTT_USERNAME", "")
    MQTT_PASSWORD: str = os.getenv("MQTT_PASSWORD", "")
    ENABLE_MQTT_SUBSCRIBER: bool = os.getenv("ENABLE_MQTT_SUBSCRIBER", "false").lower() == "true"

    # Security & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "airguard-ai-secret-key-super-secure-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Air Quality Alert Thresholds
    THRESHOLD_PM25_WARNING: float = 35.0    # ug/m3
    THRESHOLD_PM25_CRITICAL: float = 55.0   # ug/m3
    THRESHOLD_CO2_WARNING: float = 1000.0   # ppm
    THRESHOLD_CO2_CRITICAL: float = 1500.0  # ppm
    THRESHOLD_VOC_WARNING: float = 300.0    # ppb
    THRESHOLD_VOC_CRITICAL: float = 600.0   # ppb

    # CORS Settings
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]

    class Config:
        case_sensitive = True


settings = Settings()
