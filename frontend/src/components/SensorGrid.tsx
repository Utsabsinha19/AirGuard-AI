import React from "react";
import type { Telemetry } from "../types";
import { Wind, Activity, Gauge, CloudRain, Thermometer, Compass, Sun, Volume2, BatteryCharging } from "lucide-react";

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

  // Expanded sensor suite (v2.0 & v3.0 Section 1.1)
  const pressure = telemetry?.pressure ?? 1013.25;
  const light = telemetry?.ambient_light ?? 180.0;
  const noise = telemetry?.noise_level ?? 42.0;
  const battery = telemetry?.battery_pct ?? 96;

  // v3.0 Next-Gen Sensor Suite
  const hcho = telemetry?.hcho ?? 0.024;
  const pm03 = telemetry?.pm0_3 ?? 3.8;
  const pm10_val = telemetry?.pm1_0 ?? 7.2;
  const vocIndex = telemetry?.voc_index ?? 100;
  const noxIndex = telemetry?.nox_index ?? 1;
  const gasResistance = telemetry?.gas_resistance ? (telemetry.gas_resistance / 1000).toFixed(1) : "52.4";
  const cadrEstimate = telemetry?.cadr_estimate_cfm ?? 285.0;
  const filterHealth = telemetry?.filter_health_status ?? "HEALTHY_OPTIMAL";

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
      title: "HCHO Formaldehyde",
      value: hcho.toFixed(3),
      unit: "ppm",
      icon: <Activity size={18} color="#f43f5e" />,
      subtext: "WZ-S Electrochemical",
      status: hcho <= 0.05 ? "Safe" : hcho <= 0.08 ? "Off-Gas Warn" : "Hazardous",
      statusColor: hcho <= 0.05 ? "#10b981" : hcho <= 0.08 ? "#f59e0b" : "#ef4444",
      barPercent: Math.min(100, (hcho / 0.15) * 100),
    },
    {
      title: "CO₂ (Carbon Dioxide)",
      value: Math.round(co2).toString(),
      unit: "ppm",
      icon: <Activity size={18} color="#a855f7" />,
      subtext: "MH-Z19B NDIR Sensor",
      status: co2 <= 800 ? "Fresh" : co2 <= 1200 ? "Moderate" : "Stagnant",
      statusColor: co2 <= 800 ? "#10b981" : co2 <= 1200 ? "#f59e0b" : "#ef4444",
      barPercent: Math.min(100, (co2 / 2000) * 100),
    },
    {
      title: "tVOC & VOC Index",
      value: `${Math.round(voc)}`,
      unit: `ppb (Idx ${vocIndex})`,
      icon: <Gauge size={18} color="#ec4899" />,
      subtext: "SGP40 Gas Index",
      status: voc <= 200 ? "Clean" : voc <= 400 ? "Elevated" : "High",
      statusColor: voc <= 200 ? "#10b981" : voc <= 400 ? "#f59e0b" : "#ef4444",
      barPercent: Math.min(100, (voc / 800) * 100),
    },
    {
      title: "PM0.3 Ultrafine / PM1.0",
      value: `${pm03.toFixed(1)} / ${pm10_val.toFixed(1)}`,
      unit: "µg/m³",
      icon: <Wind size={18} color="#0284c7" />,
      subtext: "Sub-micron Laser",
      status: pm03 < 10 ? "Clean Air" : "Infiltration",
      statusColor: pm03 < 10 ? "#10b981" : "#f59e0b",
      barPercent: Math.min(100, (pm03 / 25) * 100),
    },
    {
      title: "NOx Combustion Index",
      value: `${noxIndex}`,
      unit: "/ 500",
      icon: <Activity size={18} color="#e11d48" />,
      subtext: "Sensirion SGP41",
      status: noxIndex <= 1 ? "Baseline" : noxIndex <= 10 ? "Flue Trace" : "Combustion",
      statusColor: noxIndex <= 1 ? "#10b981" : noxIndex <= 10 ? "#f59e0b" : "#ef4444",
      barPercent: Math.min(100, (noxIndex / 20) * 100),
    },
    {
      title: "BME688 Gas Resistance",
      value: `${gasResistance}`,
      unit: "kΩ",
      icon: <Gauge size={18} color="#8b5cf6" />,
      subtext: "AI MOX Scans",
      status: parseFloat(gasResistance) > 30 ? "Clean Matrix" : "VOC Adsorption",
      statusColor: parseFloat(gasResistance) > 30 ? "#10b981" : "#f59e0b",
      barPercent: Math.min(100, (parseFloat(gasResistance) / 100) * 100),
    },
    {
      title: "Filter CADR Decay",
      value: `${Math.round(cadrEstimate)}`,
      unit: "CFM",
      icon: <Wind size={18} color="#14b8a6" />,
      subtext: filterHealth.replace("_", " "),
      status: cadrEstimate >= 240 ? "Peak Flow" : "Filter Loaded",
      statusColor: cadrEstimate >= 240 ? "#10b981" : "#f59e0b",
      barPercent: Math.min(100, (cadrEstimate / 350) * 100),
    },
    {
      title: "Barometric Pressure",
      value: pressure.toFixed(1),
      unit: "hPa",
      icon: <Compass size={18} color="#06b6d4" />,
      subtext: "BMP280 Barometer",
      status: pressure >= 1010 ? "Stable High" : "Inversion / Low",
      statusColor: pressure >= 1010 ? "#10b981" : "#f59e0b",
      barPercent: Math.min(100, Math.max(0, ((pressure - 980) / 50) * 100)),
    },
    {
      title: "Temperature & Hum",
      value: `${temp.toFixed(1)}°C`,
      unit: `${Math.round(hum)}% RH`,
      icon: <Thermometer size={18} color="#f97316" />,
      subtext: "Sensirion SHT31",
      status: temp >= 20 && temp <= 25 ? "Comfortable" : "Unfavorable",
      statusColor: temp >= 20 && temp <= 25 ? "#10b981" : "#f59e0b",
      barPercent: Math.min(100, Math.max(0, ((temp - 10) / 25) * 100)),
    },
    {
      title: "Li-Po Battery Level",
      value: `${battery}%`,
      unit: "3.7V",
      icon: <BatteryCharging size={18} color="#10b981" />,
      subtext: "Power Management",
      status: battery > 20 ? "Operational" : "Deep Sleep Saver",
      statusColor: battery > 20 ? "#10b981" : "#ef4444",
      barPercent: battery,
    },
    {
      title: "Acoustic & Light",
      value: `${noise.toFixed(0)} dB`,
      unit: `${Math.round(light)} lux`,
      icon: <Volume2 size={18} color="#6366f1" />,
      subtext: light > 50 ? "Daytime Active" : "Night Mode",
      status: noise < 55 ? "Quiet Room" : "Active Gathering",
      statusColor: noise < 55 ? "#10b981" : "#f59e0b",
      barPercent: Math.min(100, ((noise - 30) / 60) * 100),
    },
  ];

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "14px" }}>
      {metrics.map((m, idx) => (
        <div key={idx} className="glass-panel" style={{ padding: "14px 16px", borderRadius: "14px" }}>
          
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
            <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>
              {m.title}
            </span>
            <div style={{
              width: "28px",
              height: "28px",
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
            <span className="mono-num" style={{ fontSize: "24px", fontWeight: "700", color: "#f8fafc" }}>
              {m.value}
            </span>
            <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "500" }}>
              {m.unit}
            </span>
          </div>

          {/* Progress Bar */}
          <div style={{
            height: "4px",
            width: "100%",
            borderRadius: "9999px",
            background: "rgba(255, 255, 255, 0.08)",
            overflow: "hidden",
            marginBottom: "8px"
          }}>
            <div style={{
              height: "100%",
              width: `${m.barPercent}%`,
              background: m.statusColor,
              borderRadius: "9999px",
              transition: "width 0.6s ease"
            }} />
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "10px" }}>
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
