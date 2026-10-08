import React from "react";
import { Telemetry } from "../types";
import { Wind, Activity, Gauge, CloudRain, Thermometer, ShieldAlert } from "lucide-react";

interface SensorGridProps {
  telemetry: Telemetry | null;
}

export const SensorGrid: React.FC<SensorGridProps> = ({ telemetry }) => {
  const pm25 = telemetry?.calibrated_pm2_5 ?? 10.5;
  const pm10 = telemetry?.pm10 ?? 14.8;
  const co2 = telemetry?.co2 ?? 620;
  const voc = telemetry?.calibrated_voc ?? 115;
  const temp = telemetry?.temperature ?? 22.4;
  const hum = telemetry?.humidity ?? 46.5;

  const metrics = [
    {
      title: "PM2.5 (Fine Particles)",
      value: pm25.toFixed(1),
      unit: "µg/m³",
      icon: <Wind size={18} color="#38bdf8" />,
      subtext: `Raw: ${telemetry?.pm2_5?.toFixed(1) ?? pm25.toFixed(1)} µg/m³`,
      status: pm25 <= 12 ? "Optimal" : pm25 <= 35 ? "Moderate" : "Elevated",
      statusColor: pm25 <= 12 ? "#10b981" : pm25 <= 35 ? "#f59e0b" : "#ef4444",
      barPercent: Math.min(100, (pm25 / 75) * 100),
    },
    {
      title: "CO₂ (Carbon Dioxide)",
      value: Math.round(co2).toString(),
      unit: "ppm",
      icon: <Activity size={18} color="#a855f7" />,
      subtext: "NDIR Optical Sensor",
      status: co2 <= 800 ? "Fresh" : co2 <= 1200 ? "Moderate" : "Stagnant",
      statusColor: co2 <= 800 ? "#10b981" : co2 <= 1200 ? "#f59e0b" : "#ef4444",
      barPercent: Math.min(100, (co2 / 2000) * 100),
    },
    {
      title: "tVOC (Chemical Vapors)",
      value: Math.round(voc).toString(),
      unit: "ppb",
      icon: <Gauge size={18} color="#ec4899" />,
      subtext: "SGP30 MOX Array",
      status: voc <= 200 ? "Clean" : voc <= 400 ? "Elevated" : "High",
      statusColor: voc <= 200 ? "#10b981" : voc <= 400 ? "#f59e0b" : "#ef4444",
      barPercent: Math.min(100, (voc / 800) * 100),
    },
    {
      title: "PM10 (Coarse Particulates)",
      value: pm10.toFixed(1),
      unit: "µg/m³",
      icon: <Wind size={18} color="#6366f1" />,
      subtext: "Laser Scattering",
      status: pm10 <= 54 ? "Normal" : "High",
      statusColor: pm10 <= 54 ? "#10b981" : "#f59e0b",
      barPercent: Math.min(100, (pm10 / 150) * 100),
    },
    {
      title: "Temperature",
      value: temp.toFixed(1),
      unit: "°C",
      icon: <Thermometer size={18} color="#f97316" />,
      subtext: "Sensirion SHT31",
      status: temp >= 20 && temp <= 25 ? "Comfortable" : "Unfavorable",
      statusColor: temp >= 20 && temp <= 25 ? "#10b981" : "#f59e0b",
      barPercent: Math.min(100, Math.max(0, ((temp - 10) / 25) * 100)),
    },
    {
      title: "Relative Humidity",
      value: hum.toFixed(1),
      unit: "%",
      icon: <CloudRain size={18} color="#06b6d4" />,
      subtext: "Sensirion SHT31",
      status: hum >= 35 && hum <= 60 ? "Balanced" : "Drifting",
      statusColor: hum >= 35 && hum <= 60 ? "#10b981" : "#f59e0b",
      barPercent: Math.min(100, hum),
    },
  ];

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))", gap: "16px" }}>
      {metrics.map((m, idx) => (
        <div key={idx} className="glass-panel" style={{ padding: "16px", borderRadius: "14px" }}>
          
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: "600" }}>
              {m.title}
            </span>
            <div style={{
              width: "30px",
              height: "30px",
              borderRadius: "8px",
              background: "rgba(255, 255, 255, 0.05)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}>
              {m.icon}
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "baseline", gap: "6px", marginBottom: "6px" }}>
            <span className="mono-num" style={{ fontSize: "26px", fontWeight: "700", color: "#f8fafc" }}>
              {m.value}
            </span>
            <span style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: "500" }}>
              {m.unit}
            </span>
          </div>

          {/* Progress Bar */}
          <div style={{
            height: "5px",
            width: "100%",
            borderRadius: "9999px",
            background: "rgba(255, 255, 255, 0.08)",
            overflow: "hidden",
            marginBottom: "10px"
          }}>
            <div style={{
              height: "100%",
              width: `${m.barPercent}%`,
              background: m.statusColor,
              borderRadius: "9999px",
              transition: "width 0.6s ease"
            }} />
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "11px" }}>
            <span style={{ color: "var(--text-dim)" }}>
              {m.subtext}
            </span>
            <span style={{ color: m.statusColor, fontWeight: "600" }}>
              {m.status}
            </span>
          </div>

        </div>
      ))}
    </div>
  );
};
