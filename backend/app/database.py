"""
AirGuard AI - Database Models & Async Connection Engine
Supports SQLite / PostgreSQL with time-series indexing.
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
    name = Column(String(128), nullable=False)  # "Master Bedroom Sensor"
    room = Column(String(64), nullable=False)  # "Bedroom"
    floor = Column(String(32), default="Floor 1")
    is_online = Column(Boolean, default=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    firmware_version = Column(String(32), default="v1.2.0")
    ip_address = Column(String(64), default="192.168.1.101")
    mac_address = Column(String(64), default="24:6F:28:AB:CD:01")
    created_at = Column(DateTime, default=datetime.utcnow)

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
    
    # Raw Environmental Metrics
    pm2_5 = Column(Float, nullable=False)
    pm10 = Column(Float, nullable=True)
    co2 = Column(Float, nullable=False)
    voc = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    pressure = Column(Float, default=1013.25)
    
    # Non-linear Calibrated Metrics
    calibrated_pm2_5 = Column(Float, nullable=False)
    calibrated_voc = Column(Float, nullable=False)
    
    # EPA Standard AQI & Dominant Pollutant
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
    severity = Column(String(32), nullable=False)  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
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
    horizon_mins = Column(Integer, nullable=False)  # 15, 30, 60, 360
    
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
    level = Column(String(32), nullable=False)  # "INFO", "WARNING", "CRITICAL"
    channel = Column(String(32), default="DASHBOARD")  # "DASHBOARD", "PUSH", "EMAIL", "SMS"
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
    action_type = Column(String(64), nullable=False)  # "OPEN_WINDOW", "HEPA_PURIFIER", "EXHAUST_HOOD"
    description = Column(String(255), nullable=False)
    
    initial_aqi = Column(Integer, nullable=False)
    initial_pm2_5 = Column(Float, nullable=False)
    initial_co2 = Column(Float, nullable=False)
    
    current_aqi = Column(Integer, nullable=False)
    target_aqi = Column(Integer, default=50)
    
    is_active = Column(Boolean, default=True)
    resolved_at = Column(DateTime, nullable=True)
    recovery_duration_mins = Column(Float, nullable=True)
    efficacy_score = Column(Float, nullable=True)  # Percentage recovery efficacy

    device = relationship("Device", back_populates="actions")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
