import React, { useState, useEffect } from "react";
import type { MultiModelComparisonData } from "../types";
import { fetchModelComparison } from "../api";
import { Cpu, X, CheckCircle, Zap, Activity } from "lucide-react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from "recharts";

interface ModelComparisonModalProps {
  deviceId: string;
  isOpen: boolean;
  onClose: () => void;
}

export const ModelComparisonModal: React.FC<ModelComparisonModalProps> = ({
  deviceId,
  isOpen,
  onClose,
}) => {
  const [data, setData] = useState<MultiModelComparisonData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      fetchModelComparison(deviceId)
        .then(setData)
        .catch((e) => console.error("Error loading model comparison:", e))
        .finally(() => setLoading(false));
    }
  }, [isOpen, deviceId]);

  if (!isOpen) return null;

  // Prepare chart data for multi-model trajectory overlay
  const horizons = ["+15m", "+30m", "+1h", "+6h"];
  const chartData = horizons.map((label, idx) => {
    const pt: any = { horizon: label };
    if (data) {
      data.models.forEach((m) => {
        if (m.predictions[idx]) {
          pt[m.model] = m.predictions[idx].predicted_pm2_5;
        }
      });
    }
    return pt;
  });

  const colors = ["#38bdf8", "#a855f7", "#10b981", "#f97316"];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="glass-panel"
        style={{
          width: "100%",
          maxWidth: "760px",
          maxHeight: "88vh",
          padding: "26px",
          borderRadius: "22px",
          display: "flex",
          flexDirection: "column",
          gap: "18px",
          overflowY: "auto"
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <div style={{
              background: "linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)",
              padding: "10px",
              borderRadius: "12px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}>
              <Cpu size={22} color="#ffffff" />
            </div>
            <div>
              <h3 style={{ fontSize: "19px", fontWeight: "800", color: "#ffffff" }}>
                AI Model Evolution & Multi-Architecture Benchmark (Section 2.2)
              </h3>
              <p style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                Comparing Phase A (GBM) vs Phase B Deep Sequence Models (LSTM, GRU, Temporal CNN)
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer" }}
          >
            <X size={20} />
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: "center", padding: "40px", color: "var(--text-muted)" }}>
            Running comparative multi-model inference...
          </div>
        ) : (
          <>
            {/* Benchmark Performance Comparison Table */}
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px", textAlign: "left" }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid rgba(255, 255, 255, 0.12)", color: "var(--text-muted)" }}>
                    <th style={{ padding: "8px 10px" }}>Model</th>
                    <th style={{ padding: "8px 10px" }}>Architecture</th>
                    <th style={{ padding: "8px 10px" }}>MAE (1h)</th>
                    <th style={{ padding: "8px 10px" }}>R² Score</th>
                    <th style={{ padding: "8px 10px" }}>Complexity</th>
                    <th style={{ padding: "8px 10px" }}>Latency</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.models.map((m, idx) => (
                    <tr
                      key={m.model}
                      style={{
                        borderBottom: "1px solid rgba(255, 255, 255, 0.05)",
                        background: idx % 2 === 0 ? "rgba(255, 255, 255, 0.02)" : "transparent"
                      }}
                    >
                      <td style={{ padding: "10px", fontWeight: "700", color: colors[idx] }}>
                        {m.model}
                      </td>
                      <td style={{ padding: "10px", color: "#cbd5e1" }}>{m.architecture}</td>
                      <td style={{ padding: "10px", fontWeight: "700", color: "#34d399" }} className="mono-num">
                        {m.mae_1h} µg/m³
                      </td>
                      <td style={{ padding: "10px", fontWeight: "700", color: "#38bdf8" }} className="mono-num">
                        {m.r2_1h}
                      </td>
                      <td style={{ padding: "10px", color: "var(--text-muted)" }}>{m.params}</td>
                      <td style={{ padding: "10px", color: "#fbbf24" }} className="mono-num">
                        {m.latency_ms} ms
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Comparative Trajectory Overlay Chart */}
            <div style={{
              background: "rgba(0, 0, 0, 0.25)",
              border: "1px solid rgba(255, 255, 255, 0.06)",
              borderRadius: "14px",
              padding: "16px"
            }}>
              <span style={{ fontSize: "12px", fontWeight: "700", color: "#f8fafc", display: "block", marginBottom: "12px" }}>
                Multi-Model PM2.5 Forecast Trajectory Overlay (+15m to +6h)
              </span>

              <div style={{ width: "100%", height: 240 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.06)" />
                    <XAxis dataKey="horizon" stroke="#64748b" fontSize={11} />
                    <YAxis stroke="#64748b" fontSize={11} domain={["auto", "auto"]} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#0f172a",
                        borderColor: "rgba(255, 255, 255, 0.15)",
                        borderRadius: "10px",
                        fontSize: "12px"
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                    {data?.models.map((m, idx) => (
                      <Line
                        key={m.model}
                        type="monotone"
                        dataKey={m.model}
                        stroke={colors[idx]}
                        strokeWidth={2}
                        dot={{ r: 4 }}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </>
        )}

      </div>
    </div>
  );
};
