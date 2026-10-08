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

    # Spatial Floorplan Coordinates (Section 2.3)
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
    
    # Expanded Sensor Metrics (Section 2.1)
    pressure = Column(Float, default=1013.25)
    ambient_light = Column(Float, default=150.0)
    noise_level = Column(Float, default=42.0)
    battery_pct = Column(Integer, default=95)
    
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
    channel = Column(String(32), default="DASHBOARD")
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
    target_aqi = Column(Integer, default=50)
    
    is_active = Column(Boolean, default=True)
    resolved_at = Column(DateTime, nullable=True)
    recovery_duration_mins = Column(Float, nullable=True)
    efficacy_score = Column(Float, nullable=True)

    device = relationship("Device", back_populates="actions")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
