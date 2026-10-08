import React from "react";
import type { Device, Telemetry } from "../types";
import { Compass, MapPin, Radio, Layers } from "lucide-react";

interface SpatialFloorplanProps {
  devices: Device[];
  selectedDeviceId: string;
  onSelectDevice: (id: string) => void;
  latestTelemetryMap: Record<string, Telemetry>;
}

export const SpatialFloorplan: React.FC<SpatialFloorplanProps> = ({
  devices,
  selectedDeviceId,
  onSelectDevice,
  latestTelemetryMap,
}) => {
  const getAQIColor = (aqi: number) => {
    if (aqi <= 50) return "#10b981";
    if (aqi <= 100) return "#f59e0b";
    if (aqi <= 150) return "#f97316";
    if (aqi <= 200) return "#ef4444";
    return "#a855f7";
  };

  return (
    <div className="glass-panel" style={{ padding: "24px", borderRadius: "18px", marginBottom: "20px" }}>
      
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <Layers size={20} color="#38bdf8" />
          <div>
            <h3 style={{ fontSize: "17px", fontWeight: "700", color: "#f8fafc" }}>
              Interactive Spatial Floorplan & GPS Tracking (Section 2.1, 2.3)
            </h3>
            <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
              Hyper-local indoor placement with geo-spatial mobile coordinates
            </span>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "11px", color: "var(--text-muted)" }}>
          <Compass size={14} color="#06b6d4" />
          <span>San Francisco Site: 37.7749° N, 122.4194° W</span>
        </div>
      </div>

      {/* Blueprint Floorplan Container */}
      <div style={{
        position: "relative",
        width: "100%",
        height: "260px",
        background: "radial-gradient(ellipse at center, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.95) 100%)",
        border: "1px dashed rgba(255, 255, 255, 0.15)",
        borderRadius: "14px",
        overflow: "hidden"
      }}>
        
        {/* Subtle Architectural Blueprint Grid */}
        <div style={{
          position: "absolute",
          inset: 0,
          backgroundImage: "linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px)",
          backgroundSize: "30px 30px"
        }} />

        {/* Room Nodes on Blueprint */}
        {devices.map((d) => {
          const tel = latestTelemetryMap[d.id] || d.latest_telemetry;
          const aqi = tel?.aqi ?? 45;
          const color = getAQIColor(aqi);
          const isSelected = d.id === selectedDeviceId;
          const posX = d.x_coord ?? 30;
          const posY = d.y_coord ?? 40;

          return (
            <div
              key={d.id}
              onClick={() => onSelectDevice(d.id)}
              style={{
                position: "absolute",
                left: `${posX}%`,
                top: `${posY}%`,
                transform: "translate(-50%, -50%)",
                cursor: "pointer",
                zIndex: isSelected ? 10 : 2,
                transition: "all 0.2s ease"
              }}
            >
              {/* Pulsing Aura Halo */}
              <div style={{
                position: "absolute",
                top: "50%",
                left: "50%",
                transform: "translate(-50%, -50%)",
                width: isSelected ? "110px" : "80px",
                height: isSelected ? "110px" : "80px",
                borderRadius: "50%",
                background: color,
                opacity: isSelected ? 0.28 : 0.14,
                filter: "blur(18px)",
                pointerEvents: "none"
              }} />

              {/* Node Card */}
              <div style={{
                background: isSelected ? "rgba(15, 23, 42, 0.95)" : "rgba(30, 41, 59, 0.85)",
                border: `2px solid ${isSelected ? "#38bdf8" : color}`,
                borderRadius: "12px",
                padding: "8px 12px",
                minWidth: "130px",
                boxShadow: isSelected ? "0 0 20px rgba(56, 189, 248, 0.4)" : "0 4px 12px rgba(0,0,0,0.5)",
                display: "flex",
                flexDirection: "column",
                gap: "2px"
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: "11px", fontWeight: "700", color: "#f8fafc" }}>
                    {d.room}
                  </span>
                  <div style={{ width: "6px", height: "6px", borderRadius: "50%", background: color }} />
                </div>

                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginTop: "2px" }}>
                  <span className="mono-num" style={{ fontSize: "16px", fontWeight: "800", color: "#ffffff" }}>
                    {aqi} <span style={{ fontSize: "10px", color: "var(--text-muted)", fontWeight: "500" }}>AQI</span>
                  </span>
                  <span style={{ fontSize: "10px", color: "var(--text-dim)" }}>
                    {d.id}
                  </span>
                </div>

                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "9px", color: "var(--text-muted)", marginTop: "1px" }}>
                  <span>PM: {tel?.calibrated_pm2_5?.toFixed(1) ?? "9.0"}</span>
                  <span>{tel?.temperature?.toFixed(1) ?? "22"}°C</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
};
