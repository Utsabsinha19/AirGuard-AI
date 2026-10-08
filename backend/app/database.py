"""
AirGuard AI - Database Models & Async Connection Engine (FR-3.2, Section 2.1, 2.3)
Enhanced with expanded sensor parameters, spatial floorplan coordinates,
and device-level calibration settings.
"""

from datetime import datetime
from typing import AsyncGenerator
from sqlalchemy import (
    Column, Integer, Float, String, Boolean, DateTime,
    ForeignKey, Text, Index, JSON
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.config import settings

Base = declarative_base()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


class Device(Base):
    __tablename__ = "devices"

    id = Column(String(64), primary_key=True)  # e.g., "AG-001"
    name = Column(String(128), nullable=False)
    room = Column(String(64), nullable=False)
    floor = Column(String(32), default="Floor 1")
    is_online = Column(Boolean, default=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    firmware_version = Column(String(32), default="v1.3.0-EXP")
    ip_address = Column(String(64), default="192.168.1.101")
    mac_address = Column(String(64), default="24:6F:28:AB:CD:01")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Spatial Floorplan Coordinates & Zone Topology (Section 2.3, 4.1)
    zone = Column(String(64), default="Indoor")  # e.g., Bedroom, Living Room, Nursery, Office, Outdoor
    x_coord = Column(Float, default=25.0)  # Percentage X on 2D floorplan (0 - 100)
    y_coord = Column(Float, default=30.0)  # Percentage Y on 2D floorplan (0 - 100)
    latitude = Column(Float, default=37.7749)
    longitude = Column(Float, default=-122.4194)

    # Localized Calibration Factors (Section 2.2 Suggestion 3)
    pm_zero_offset = Column(Float, default=0.0)
    pm_gain = Column(Float, default=1.0)
    voc_zero_offset = Column(Float, default=0.0)
    voc_gain = Column(Float, default=1.0)

    # Relationships
    telemetry = relationship("Telemetry", back_populates="device", cascade="all, delete-orphan")
    anomalies = relationship("Anomaly", back_populates="device", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="device", cascade="all, delete-orphan")
    actions = relationship("RemediationAction", back_populates="device", cascade="all, delete-orphan")


class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(64), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Primary Metrics
    pm2_5 = Column(Float, nullable=False)
    pm10 = Column(Float, nullable=True)
    co2 = Column(Float, nullable=False)
    voc = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    
    # Expanded Sensor Metrics (Section 2.1 & v3.0)
    pressure = Column(Float, default=1013.25)
    ambient_light = Column(Float, default=150.0)
    noise_level = Column(Float, default=42.0)
    battery_pct = Column(Integer, default=95)
    
    # Next-Gen Sensor Matrix (v3.0 Section 1.1)
    pm0_3 = Column(Float, default=0.0)
    pm1_0 = Column(Float, default=0.0)
    hcho = Column(Float, default=0.0)                 # Electrochemical Formaldehyde in ppm
    voc_index = Column(Float, default=100.0)          # Sensirion VOC Index 0-500
    nox_index = Column(Float, default=1.0)            # Sensirion NOx Index 0-500
    gas_resistance = Column(Float, default=50000.0)   # BME688 Gas Resistance in Ohms
    
    # Non-linear Calibrated Metrics
    calibrated_pm2_5 = Column(Float, nullable=False)
    calibrated_voc = Column(Float, nullable=False)
    
    # EPA Standard AQI
    aqi = Column(Integer, nullable=False)
    aqi_category = Column(String(64), nullable=False)
    dominant_pollutant = Column(String(32), default="PM2.5")

    device = relationship("Device", back_populates="telemetry")

    __table_args__ = (
        Index("idx_device_timestamp", "device_id", "timestamp"),
    )


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(64), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    anomaly_score = Column(Float, nullable=False)
    severity = Column(String(32), nullable=False)
    root_cause_code = Column(String(64), nullable=False)
    root_cause_title = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    sensor_contributions = Column(JSON, nullable=True)
    is_resolved = Column(Boolean, default=False)

    device = relationship("Device", back_populates="anomalies")


class PredictionRecord(Base):
    __tablename__ = "prediction_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(64), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    horizon_mins = Column(Integer, nullable=False)
    
    predicted_pm2_5 = Column(Float, nullable=False)
    predicted_co2 = Column(Float, nullable=False)
    predicted_voc = Column(Float, nullable=False)
    predicted_aqi = Column(Integer, nullable=False)
    aqi_category = Column(String(64), nullable=False)
    
    confidence_lower = Column(Float, nullable=False)
    confidence_upper = Column(Float, nullable=False)
    model_type = Column(String(64), default="GradientBoosting")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(64), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    level = Column(String(32), nullable=False)
    channel = Column(String(64), default="DASHBOARD")
    channels = Column(String(128), default="WEB_DASHBOARD_TOAST,APP_PUSH")
    title = Column(String(128), nullable=False)
    message = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=True)
    acknowledged = Column(Boolean, default=False)

    device = relationship("Device", back_populates="alerts")


class RemediationAction(Base):
    __tablename__ = "remediation_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(64), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    action_type = Column(String(64), nullable=False)
    description = Column(String(255), nullable=False)
    
    initial_aqi = Column(Integer, nullable=False)
    initial_pm2_5 = Column(Float, nullable=False)
    initial_co2 = Column(Float, nullable=False)
    
    current_aqi = Column(Integer, nullable=False)
    current_pm2_5 = Column(Float, nullable=True)
    current_co2 = Column(Float, nullable=True)
    target_aqi = Column(Integer, default=50)
    
    # Real-Time Recovery & Decay Metrics (Section 4.2 & v3.0 Exponential CADR Model)
    co2_decay_rate = Column(Float, nullable=True)        # ppm / min
    pm25_decay_rate = Column(Float, nullable=True)       # µg/m³ / min
    decay_constant_k = Column(Float, nullable=True)      # Exponential decay constant k (min^-1)
    cadr_estimate_cfm = Column(Float, nullable=True)     # Clean Air Delivery Rate in CFM
    filter_health_status = Column(String(64), default="NOMINAL")  # "NOMINAL", "DEGRADED", "CLOGGED"
    recovery_message = Column(String(255), nullable=True)
    
    is_active = Column(Boolean, default=True)
    resolved_at = Column(DateTime, nullable=True)
    recovery_duration_mins = Column(Float, nullable=True)
    efficacy_score = Column(Float, nullable=True)

    device = relationship("Device", back_populates="actions")


# ---------------------------------------------------------------------------
# Version 3.0 Smart Home Actuation Models (Matter / Home Assistant)
# ---------------------------------------------------------------------------

class ActuatorDevice(Base):
    __tablename__ = "actuator_devices"

    id = Column(String(64), primary_key=True)            # e.g., "PURIFIER-01", "HVAC-DAMPER-01"
    name = Column(String(128), nullable=False)
    room = Column(String(64), nullable=False)
    device_type = Column(String(64), nullable=False)     # "SMART_PURIFIER", "HVAC_DAMPER", "MOTORIZED_WINDOW"
    protocol = Column(String(32), default="MATTER")      # "MATTER", "HOME_ASSISTANT"
    is_online = Column(Boolean, default=True)
    state = Column(String(64), default="AUTO")           # "ON", "OFF", "AUTO", "OPEN", "CLOSED"
    fan_speed = Column(String(32), default="AUTO")       # "OFF", "LOW", "MED", "HIGH", "BOOST", "AUTO"
    damper_position = Column(Integer, default=50)        # 0 - 100%
    window_open_pct = Column(Integer, default=0)         # 0 - 100%
    auto_mode = Column(Boolean, default=True)
    last_actuated_at = Column(DateTime, default=datetime.utcnow)


class ActuationLog(Base):
    __tablename__ = "actuation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    actuator_id = Column(String(64), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    trigger_type = Column(String(64), nullable=False)   # "PREEMPTIVE_ML", "THRESHOLD_ANOMALY", "MANUAL_OVERRIDE"
    action_taken = Column(String(128), nullable=False)
    reason = Column(String(255), nullable=False)
    status = Column(String(32), default="SUCCESS")


class UserHealthProfile(Base):
    __tablename__ = "user_health_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), default="default_user", unique=True, index=True)
    profile_type = Column(String(64), default="STANDARD")  # "STANDARD", "ASTHMATIC", "CARDIOVASCULAR", "PEDIATRIC", "ELDERLY"
    minute_ventilation_rate = Column(Float, default=12.0)  # L/min
    target_pm25_limit = Column(Float, default=15.0)        # µg/m³ (WHO target)
    target_co2_limit = Column(Float, default=1000.0)       # ppm
    target_hcho_limit = Column(Float, default=0.08)        # ppm
    updated_at = Column(DateTime, default=datetime.utcnow)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
