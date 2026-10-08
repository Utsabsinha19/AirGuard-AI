import React, { useState } from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";
import { Telemetry, PredictionData } from "../types";
import { TrendingUp, Clock, ShieldCheck } from "lucide-react";

interface ForecastChartProps {
  history: Telemetry[];
  predictions: PredictionData | null;
  modelType: string;
}

export const ForecastChart: React.FC<ForecastChartProps> = ({
  history,
  predictions,
  modelType,
}) => {
  const [selectedMetric, setSelectedMetric] = useState<"pm2_5" | "co2" | "voc" | "aqi">("pm2_5");

  // Prepare combined timeline dataset: historical points followed by forecasted future points
  const chartData: any[] = [];

  // 1. Add historical points (last 15-20 points)
  const recentHistory = history.slice(-20);
  recentHistory.forEach((h) => {
    const d = new Date(h.timestamp);
    const timeLabel = d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    chartData.push({
      time: timeLabel,
      actual_pm2_5: h.calibrated_pm2_5,
      actual_co2: h.co2,
      actual_voc: h.calibrated_voc,
      actual_aqi: h.aqi,
      isForecast: false,
    });
  });

  // 2. Add forecast points (+15m, +30m, +60m, +360m)
  if (predictions && predictions.predictions.length > 0) {
    const lastHistoryPoint = chartData[chartData.length - 1];

    predictions.predictions.forEach((p) => {
      chartData.push({
        time: p.horizon_label,
        predicted_pm2_5: p.predicted_pm2_5,
        predicted_co2: p.predicted_co2,
        predicted_voc: p.predicted_voc,
        predicted_aqi: p.predicted_aqi,
        ci_lower: p.confidence_lower,
        ci_upper: p.confidence_upper,
        ci_range: [p.confidence_lower, p.confidence_upper],
        isForecast: true,
      });
    });
  }

  const metricConfigs = {
    pm2_5: {
      label: "PM2.5 Particulate",
      unit: "µg/m³",
      actualKey: "actual_pm2_5",
      predKey: "predicted_pm2_5",
      color: "#38bdf8",
      predColor: "#06b6d4",
      ciColor: "#0284c7",
    },
    co2: {
      label: "Carbon Dioxide",
      unit: "ppm",
      actualKey: "actual_co2",
      predKey: "predicted_co2",
      color: "#a855f7",
      predColor: "#c084fc",
      ciColor: "#9333ea",
    },
    voc: {
      label: "tVOC Vapors",
      unit: "ppb",
      actualKey: "actual_voc",
      predKey: "predicted_voc",
      color: "#f43f5e",
      predColor: "#fb7185",
      ciColor: "#e11d48",
    },
    aqi: {
      label: "Composite AQI",
      unit: "Index",
      actualKey: "actual_aqi",
      predKey: "predicted_aqi",
      color: "#10b981",
      predColor: "#34d399",
      ciColor: "#059669",
    },
  };

  const currentCfg = metricConfigs[selectedMetric];

  return (
    <div className="glass-panel" style={{ padding: "24px", borderRadius: "18px" }}>
      
      {/* Header & Controls */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px", marginBottom: "18px" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <TrendingUp size={20} color="#38bdf8" />
            <h3 style={{ fontSize: "17px", fontWeight: "700", color: "#f8fafc" }}>
              Multi-Horizon AI Trajectory & Forecasting (FR-4)
            </h3>
          </div>
          <p style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>
            Seamless historical trend lines with +15m, +30m, +1h, and +6h projections & confidence bounds
          </p>
        </div>

        {/* Metric Selector Pills */}
        <div style={{
          display: "flex",
          gap: "4px",
          background: "rgba(255, 255, 255, 0.05)",
          padding: "4px",
          borderRadius: "10px",
          border: "1px solid rgba(255, 255, 255, 0.08)"
        }}>
          {(["pm2_5", "co2", "voc", "aqi"] as const).map((m) => (
            <button
              key={m}
              onClick={() => setSelectedMetric(m)}
              style={{
                background: selectedMetric === m ? "rgba(255, 255, 255, 0.15)" : "transparent",
                color: selectedMetric === m ? "#ffffff" : "var(--text-muted)",
                border: "none",
                borderRadius: "6px",
                padding: "6px 12px",
                fontSize: "12px",
                fontWeight: "600",
                cursor: "pointer",
                transition: "all 0.15s ease"
              }}
            >
              {m.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Horizon Summary Badges */}
      {predictions && (
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
          gap: "10px",
          marginBottom: "18px"
        }}>
          {predictions.predictions.map((p) => (
            <div key={p.horizon_mins} style={{
              background: "rgba(255, 255, 255, 0.03)",
              border: "1px solid rgba(255, 255, 255, 0.07)",
              borderRadius: "12px",
              padding: "10px 12px",
              display: "flex",
              flexDirection: "column",
              gap: "4px"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "11px", fontWeight: "700", color: "#38bdf8" }}>
                  {p.horizon_label}
                </span>
                <span style={{
                  fontSize: "10px",
                  fontWeight: "700",
                  color: p.aqi_color,
                  background: `${p.aqi_color}18`,
                  padding: "1px 6px",
                  borderRadius: "4px"
                }}>
                  {p.aqi_category}
                </span>
              </div>
              <div style={{ display: "flex", alignItems: "baseline", gap: "4px" }}>
                <span className="mono-num" style={{ fontSize: "18px", fontWeight: "700", color: "#ffffff" }}>
                  {selectedMetric === "pm2_5" ? p.predicted_pm2_5 :
                   selectedMetric === "co2" ? p.predicted_co2 :
                   selectedMetric === "voc" ? p.predicted_voc : p.predicted_aqi}
                </span>
                <span style={{ fontSize: "11px", color: "var(--text-dim)" }}>
                  {currentCfg.unit}
                </span>
              </div>
              {selectedMetric === "pm2_5" && (
                <span style={{ fontSize: "10px", color: "var(--text-muted)" }}>
                  95% CI: [{p.confidence_lower} – {p.confidence_upper}]
                </span>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Recharts Chart Canvas */}
      <div style={{ width: "100%", height: 320 }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="actualGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={currentCfg.color} stopOpacity={0.3} />
                <stop offset="95%" stopColor={currentCfg.color} stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="ciGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={currentCfg.ciColor} stopOpacity={0.25} />
                <stop offset="95%" stopColor={currentCfg.ciColor} stopOpacity={0.05} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.06)" />
            <XAxis dataKey="time" stroke="#64748b" fontSize={11} tickLine={false} />
            <YAxis stroke="#64748b" fontSize={11} tickLine={false} domain={["auto", "auto"]} />
            
            <Tooltip
              contentStyle={{
                backgroundColor: "#0f172a",
                borderColor: "rgba(255, 255, 255, 0.15)",
                borderRadius: "10px",
                fontSize: "12px",
                color: "#ffffff"
              }}
            />

            {/* Historical Area */}
            <Area
              type="monotone"
              dataKey={currentCfg.actualKey}
              stroke={currentCfg.color}
              strokeWidth={2.5}
              fill="url(#actualGradient)"
              name={`Actual ${currentCfg.label}`}
              connectNulls={true}
            />

            {/* Shaded Confidence Interval (for PM2.5) */}
            {selectedMetric === "pm2_5" && (
              <Area
                type="monotone"
                dataKey="ci_upper"
                stroke="transparent"
                fill="url(#ciGradient)"
                name="95% Confidence Upper"
                connectNulls={true}
              />
            )}

            {/* Predicted Trajectory Line */}
            <Line
              type="monotone"
              dataKey={currentCfg.predKey}
              stroke={currentCfg.predColor}
              strokeWidth={2.5}
              strokeDasharray="5 5"
              name={`Forecasted ${currentCfg.label}`}
              dot={{ r: 4, fill: currentCfg.predColor }}
              connectNulls={true}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

    </div>
  );
};
