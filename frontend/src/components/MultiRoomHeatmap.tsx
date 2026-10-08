import React from "react";
import { Device, Telemetry } from "../types";
import { Home, Layers, CheckCircle2, AlertTriangle } from "lucide-react";

interface MultiRoomHeatmapProps {
  devices: Device[];
  selectedDeviceId: string;
  onSelectDevice: (id: string) => void;
  latestTelemetryMap: Record<string, Telemetry>;
}

export const MultiRoomHeatmap: React.FC<MultiRoomHeatmapProps> = ({
  devices,
  selectedDeviceId,
  onSelectDevice,
  latestTelemetryMap,
}) => {
  const getCategoryColor = (aqi: number) => {
    if (aqi <= 50) return "#10b981";
    if (aqi <= 100) return "#f59e0b";
    if (aqi <= 150) return "#f97316";
    if (aqi <= 200) return "#ef4444";
    return "#a855f7";
  };

  return (
    <div className="glass-panel" style={{ padding: "24px", borderRadius: "18px" }}>
      
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <Layers size={20} color="#a855f7" />
          <h3 style={{ fontSize: "17px", fontWeight: "700", color: "#f8fafc" }}>
            Multi-Room Spatial Zone Grid (US-05)
          </h3>
        </div>
        <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
          {devices.length} Nodes Active
        </span>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "14px" }}>
        {devices.map((dev) => {
          const tel = latestTelemetryMap[dev.id] || dev.latest_telemetry;
          const aqi = tel?.aqi ?? 45;
          const cat = tel?.aqi_category ?? "Good";
          const color = getCategoryColor(aqi);
          const isSelected = dev.id === selectedDeviceId;

          return (
            <div
              key={dev.id}
              onClick={() => onSelectDevice(dev.id)}
              style={{
                background: isSelected ? "rgba(99, 102, 241, 0.12)" : "rgba(255, 255, 255, 0.03)",
                border: `1.5px solid ${isSelected ? "#6366f1" : "rgba(255, 255, 255, 0.08)"}`,
                borderRadius: "14px",
                padding: "16px",
                cursor: "pointer",
                transition: "all 0.2s ease",
                position: "relative",
                overflow: "hidden"
              }}
            >
              {/* Corner accent glow */}
              <div style={{
                position: "absolute",
                top: 0,
                right: 0,
                width: "60px",
                height: "60px",
                background: color,
                filter: "blur(40px)",
                opacity: 0.2,
                pointerEvents: "none"
              }} />

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
                <div>
                  <h4 style={{ fontSize: "15px", fontWeight: "700", color: "#ffffff" }}>
                    {dev.room}
                  </h4>
                  <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                    {dev.id} • {dev.floor}
                  </span>
                </div>

                <div style={{
                  padding: "2px 8px",
                  borderRadius: "6px",
                  background: `${color}20`,
                  border: `1px solid ${color}44`,
                  color: color,
                  fontSize: "11px",
                  fontWeight: "700"
                }}>
                  {cat}
                </div>
              </div>

              {/* Big Score & Details */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginTop: "12px" }}>
                <div>
                  <span className="mono-num" style={{ fontSize: "28px", fontWeight: "800", color: "#ffffff" }}>
                    {aqi}
                  </span>
                  <span style={{ fontSize: "11px", color: "var(--text-muted)", marginLeft: "4px" }}>
                    AQI
                  </span>
                </div>

                <div style={{ textAlign: "right", fontSize: "11px", color: "var(--text-dim)" }}>
                  <div>PM2.5: {tel?.calibrated_pm2_5?.toFixed(1) ?? "10.0"}</div>
                  <div>CO₂: {Math.round(tel?.co2 ?? 600)} ppm</div>
                </div>
              </div>

              {isSelected && (
                <div style={{
                  marginTop: "10px",
                  fontSize: "10px",
                  fontWeight: "700",
                  color: "#818cf8",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em"
                }}>
                  ● Viewing Room Details
                </div>
              )}
            </div>
          );
        })}
      </div>

    </div>
  );
};
