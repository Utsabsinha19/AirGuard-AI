import React, { useState, useEffect } from "react";
import { Network, Wind, ArrowRight, Activity, Layers, ShieldCheck, Compass, RefreshCw } from "lucide-react";
import type { CrossRoomDiffusionResponse, RoomDiffusionNode, DiffusionEdge } from "../types";
import { fetchCrossRoomDiffusion } from "../api";

interface CrossRoomDiffusionStudioProps {
  onSelectRoom?: (roomId: string) => void;
}

export const CrossRoomDiffusionStudio: React.FC<CrossRoomDiffusionStudioProps> = ({ onSelectRoom }) => {
  const [data, setData] = useState<CrossRoomDiffusionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [horizonView, setHorizonView] = useState<"15m" | "30m" | "60m">("30m");

  const loadDiffusion = async () => {
    setLoading(true);
    try {
      const res = await fetchCrossRoomDiffusion();
      setData(res);
    } catch (e) {
      console.error("Failed to load cross-room diffusion:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDiffusion();
    const interval = setInterval(loadDiffusion, 15000);
    return () => clearInterval(interval);
  }, []);

  const getAQIColor = (aqi: number) => {
    if (aqi <= 50) return "#10b981";
    if (aqi <= 100) return "#f59e0b";
    if (aqi <= 150) return "#f97316";
    return "#ef4444";
  };

  return (
    <div className="glass-panel" style={{ padding: "20px", borderRadius: "16px", marginTop: "16px" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", flexWrap: "wrap", gap: "10px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div style={{
            width: "36px",
            height: "36px",
            borderRadius: "10px",
            background: "linear-gradient(135deg, rgba(168, 85, 247, 0.2), rgba(236, 72, 153, 0.2))",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            border: "1px solid rgba(168, 85, 247, 0.3)"
          }}>
            <Network size={20} color="#c084fc" />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <h3 style={{ fontSize: "16px", fontWeight: "700", color: "#f8fafc", margin: 0 }}>
                ST-GNN Spatio-Temporal Diffusion Studio
              </h3>
              <span style={{
                fontSize: "10px",
                padding: "2px 8px",
                borderRadius: "12px",
                background: "rgba(168, 85, 247, 0.15)",
                color: "#c084fc",
                border: "1px solid rgba(168, 85, 247, 0.3)",
                fontWeight: "600"
              }}>
                Graph Laplacian Heat Kernel
              </span>
            </div>
            <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: "2px 0 0 0" }}>
              Models cross-room airborne particulate advection, door gaps & HVAC duct diffusion
            </p>
          </div>
        </div>

        {/* Horizon Selector */}
        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <span style={{ fontSize: "11px", color: "var(--text-muted)", marginRight: "4px" }}>Projection:</span>
          {(["15m", "30m", "60m"] as const).map((h) => (
            <button
              key={h}
              onClick={() => setHorizonView(h)}
              style={{
                padding: "4px 10px",
                borderRadius: "6px",
                fontSize: "11px",
                fontWeight: "600",
                border: "1px solid",
                borderColor: horizonView === h ? "#a855f7" : "rgba(255, 255, 255, 0.1)",
                background: horizonView === h ? "rgba(168, 85, 247, 0.2)" : "rgba(255, 255, 255, 0.03)",
                color: horizonView === h ? "#f8fafc" : "var(--text-muted)",
                cursor: "pointer",
              }}
            >
              +{h}
            </button>
          ))}

          <button
            onClick={loadDiffusion}
            style={{
              padding: "4px 8px",
              borderRadius: "6px",
              background: "rgba(255, 255, 255, 0.05)",
              color: "var(--text-muted)",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              cursor: "pointer",
              marginLeft: "4px"
            }}
          >
            <RefreshCw size={12} className={loading ? "spin-animate" : ""} />
          </button>
        </div>
      </div>

      {/* Diffusion Summary Banner */}
      {data?.summary && (
        <div style={{
          padding: "10px 14px",
          borderRadius: "10px",
          background: "rgba(168, 85, 247, 0.08)",
          border: "1px solid rgba(168, 85, 247, 0.25)",
          color: "#e2e8f0",
          fontSize: "12px",
          marginBottom: "16px",
          display: "flex",
          alignItems: "center",
          gap: "8px"
        }}>
          <Activity size={16} color="#c084fc" />
          <span>{data.summary}</span>
        </div>
      )}

      {/* Room Nodes Spatial Flow Grid */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
        gap: "12px",
        marginBottom: "16px"
      }}>
        {data?.nodes.map((node) => {
          const projectedVal =
            horizonView === "15m"
              ? node.projected_pm2_5_15m
              : horizonView === "30m"
              ? node.projected_pm2_5_30m
              : node.projected_pm2_5_60m;

          const delta = projectedVal - node.current_pm2_5;
          const aqiColor = getAQIColor(node.current_aqi);

          return (
            <div
              key={node.room_id}
              onClick={() => onSelectRoom?.(node.room_id)}
              style={{
                padding: "14px",
                borderRadius: "12px",
                background: "rgba(15, 23, 42, 0.7)",
                border: "1px solid rgba(255, 255, 255, 0.08)",
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
                <div>
                  <div style={{ fontSize: "14px", fontWeight: "700", color: "#f8fafc" }}>
                    {node.name}
                  </div>
                  <div style={{ fontSize: "10px", color: "var(--text-muted)" }}>
                    {node.zone} • {node.room_id}
                  </div>
                </div>

                <span style={{
                  fontSize: "11px",
                  fontWeight: "700",
                  padding: "2px 8px",
                  borderRadius: "8px",
                  background: `${aqiColor}22`,
                  color: aqiColor,
                  border: `1px solid ${aqiColor}44`
                }}>
                  AQI {node.current_aqi}
                </span>
              </div>

              {/* Current vs Projected PM2.5 */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: "8px" }}>
                <div>
                  <span style={{ fontSize: "10px", color: "var(--text-muted)", display: "block" }}>Current PM2.5</span>
                  <span className="mono-num" style={{ fontSize: "18px", fontWeight: "700", color: "#f8fafc" }}>
                    {node.current_pm2_5.toFixed(1)} <span style={{ fontSize: "10px" }}>µg/m³</span>
                  </span>
                </div>

                <div style={{ textAlign: "right" }}>
                  <span style={{ fontSize: "10px", color: "var(--text-muted)", display: "block" }}>
                    +{horizonView} Forecast
                  </span>
                  <span className="mono-num" style={{
                    fontSize: "18px",
                    fontWeight: "700",
                    color: delta > 2 ? "#ef4444" : delta < -2 ? "#10b981" : "#f8fafc"
                  }}>
                    {projectedVal.toFixed(1)}
                  </span>
                </div>
              </div>

              {/* Diffusion Flow Direction Badge */}
              <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "6px 8px",
                borderRadius: "6px",
                background: "rgba(0, 0, 0, 0.3)",
                fontSize: "10px"
              }}>
                <span style={{ color: "var(--text-muted)" }}>Spatial Dynamic:</span>
                <span style={{
                  fontWeight: "600",
                  color:
                    node.risk_direction === "DIFFUSING_OUTWARD"
                      ? "#f97316"
                      : node.risk_direction === "RECEIVING_INFLOW"
                      ? "#eab308"
                      : "#10b981"
                }}>
                  {node.risk_direction.replace("_", " ")}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Advection Transfer Channels / Graph Edges */}
      <div>
        <div style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-muted)", marginBottom: "8px", display: "flex", alignItems: "center", gap: "6px" }}>
          <Layers size={13} color="#a855f7" /> Cross-Room Transport Edges & Flux Coefficients
        </div>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
          gap: "8px"
        }}>
          {data?.edges.map((edge, idx) => (
            <div
              key={idx}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "8px 12px",
                borderRadius: "8px",
                background: "rgba(255, 255, 255, 0.02)",
                border: "1px solid rgba(255, 255, 255, 0.05)",
                fontSize: "11px"
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span style={{ fontWeight: "600", color: "#38bdf8" }}>{edge.source_room}</span>
                <ArrowRight size={12} color="var(--text-muted)" />
                <span style={{ fontWeight: "600", color: "#c084fc" }}>{edge.target_room}</span>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{
                  fontSize: "9px",
                  padding: "2px 6px",
                  borderRadius: "4px",
                  background: "rgba(255, 255, 255, 0.06)",
                  color: "var(--text-muted)"
                }}>
                  {edge.transport_channel.replace("_", " ")}
                </span>
                <span style={{ color: "#f59e0b", fontWeight: "700" }}>
                  {edge.flux_rate_pct.toFixed(0)}% Flux
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
