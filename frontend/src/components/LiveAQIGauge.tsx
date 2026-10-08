import React from "react";
import { Telemetry } from "../types";
import { ShieldCheck, AlertTriangle, Flame, Droplets, Wind } from "lucide-react";

interface LiveAQIGaugeProps {
  telemetry: Telemetry | null;
  roomName: string;
}

export const LiveAQIGauge: React.FC<LiveAQIGaugeProps> = ({ telemetry, roomName }) => {
  const aqi = telemetry?.aqi ?? 42;
  const category = telemetry?.aqi_category ?? "Good";
  const dominant = telemetry?.dominant_pollutant ?? "PM2.5";
  const color = telemetry?.aqi_color ?? "#10b981";

  // Compute SVG arc circumference for semi-circle gauge (radius=85)
  const radius = 80;
  const stroke = 14;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  // Map AQI (0 to 300) to 0 to 1 progress
  const progress = Math.min(1.0, Math.max(0.0, aqi / 300.0));
  const strokeDashoffset = circumference - progress * (circumference / 2);

  const getHealthAdvice = (cat: string) => {
    switch (cat.toLowerCase()) {
      case "good":
        return "Indoor air quality is optimal. Respiration conditions are ideal for all occupants.";
      case "moderate":
        return "Air quality is acceptable. Sensitive individuals should consider gentle ventilation.";
      case "unhealthy for sensitive groups":
        return "Fine particulates or gases elevated. Activate air purifiers on low/medium.";
      case "unhealthy":
        return "Active pollution detected. Increase fresh air ventilation or run HEPA purifiers on high.";
      case "very unhealthy":
        return "Severe pollution event. Isolate the room and run maximum filtration immediately.";
      default:
        return "Hazardous indoor atmosphere. Evacuate room or run emergency ventilation.";
    }
  };

  return (
    <div className="glass-panel" style={{ padding: "24px", position: "relative", overflow: "hidden" }}>
      
      {/* Background Ambient Glow */}
      <div style={{
        position: "absolute",
        top: "-40px",
        right: "-40px",
        width: "180px",
        height: "180px",
        borderRadius: "50%",
        background: color,
        filter: "blur(75px)",
        opacity: 0.18,
        pointerEvents: "none"
      }} />

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
        <div>
          <span style={{ fontSize: "11px", textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--text-muted)", fontWeight: "700" }}>
            Localized Real-Time AQI
          </span>
          <h2 style={{ fontSize: "20px", fontWeight: "700", color: "#f8fafc", marginTop: "2px" }}>
            {roomName}
          </h2>
        </div>

        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "6px",
          padding: "4px 10px",
          borderRadius: "8px",
          background: "rgba(255, 255, 255, 0.05)",
          border: "1px solid rgba(255, 255, 255, 0.1)"
        }}>
          <span style={{ fontSize: "11px", color: "#38bdf8", fontWeight: "600" }}>
            Hygroscopic Calibrated
          </span>
        </div>
      </div>

      {/* Radial Meter & Big Score */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", margin: "10px 0" }}>
        <div style={{ position: "relative", width: "200px", height: "120px", display: "flex", justifyContent: "center" }}>
          
          <svg height="160" width="200" style={{ transform: "rotate(-180deg)" }}>
            {/* Background Arc */}
            <circle
              stroke="rgba(255, 255, 255, 0.08)"
              fill="transparent"
              strokeWidth={stroke}
              strokeDasharray={circumference + " " + circumference}
              style={{ strokeDashoffset: circumference / 2 }}
              strokeLinecap="round"
              r={normalizedRadius}
              cx="100"
              cy="80"
            />
            {/* Value Arc */}
            <circle
              stroke={color}
              fill="transparent"
              strokeWidth={stroke}
              strokeDasharray={circumference + " " + circumference}
              style={{
                strokeDashoffset: strokeDashoffset,
                transition: "stroke-dashoffset 0.8s ease, stroke 0.5s ease",
              }}
              strokeLinecap="round"
              r={normalizedRadius}
              cx="100"
              cy="80"
            />
          </svg>

          {/* Central Readout */}
          <div style={{
            position: "absolute",
            bottom: "8px",
            textAlign: "center"
          }}>
            <span className="mono-num" style={{
              fontSize: "44px",
              fontWeight: "800",
              color: "#ffffff",
              letterSpacing: "-0.03em",
              textShadow: `0 0 20px ${color}66`
            }}>
              {aqi}
            </span>
            <span style={{ fontSize: "13px", color: "var(--text-muted)", marginLeft: "4px", fontWeight: "600" }}>
              AQI
            </span>
          </div>
        </div>

        {/* Status Badge */}
        <div style={{
          marginTop: "6px",
          display: "inline-flex",
          alignItems: "center",
          gap: "8px",
          padding: "6px 16px",
          borderRadius: "9999px",
          background: `${color}22`,
          border: `1px solid ${color}66`,
          boxShadow: `0 0 12px ${color}33`
        }}>
          <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: color }} />
          <span style={{ fontSize: "13px", fontWeight: "700", color: "#f8fafc" }}>
            {category}
          </span>
        </div>
      </div>

      {/* Dominant Pollutant & Advice Box */}
      <div style={{
        marginTop: "18px",
        padding: "12px 14px",
        borderRadius: "12px",
        background: "rgba(255, 255, 255, 0.03)",
        border: "1px solid rgba(255, 255, 255, 0.06)"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
          <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>
            Dominant Factor:
          </span>
          <span style={{ fontSize: "12px", color: "#f8fafc", fontWeight: "700", background: "rgba(255, 255, 255, 0.08)", padding: "2px 8px", borderRadius: "6px" }}>
            {dominant}
          </span>
        </div>
        <p style={{ fontSize: "12px", color: "#cbd5e1", lineHeight: "1.45" }}>
          {getHealthAdvice(category)}
        </p>
      </div>

    </div>
  );
};
