import React, { useState, useEffect } from "react";
import {
  Zap,
  TrendingDown,
  Sun,
  Clock,
  Sparkles,
  DollarSign,
  Activity,
  Layers,
  CheckCircle2,
  AlertTriangle
} from "lucide-react";
import type { GridOptimizationStatus } from "../types";
import { fetchGridTariffs, evaluateGridDemandResponse } from "../api";

export const GridDemandResponseCard: React.FC = () => {
  const [gridStatus, setGridStatus] = useState<GridOptimizationStatus | null>(null);
  const [tariffInfo, setTariffInfo] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchGridTariffs().then(setTariffInfo).catch(console.error);
    evaluateGridDemandResponse(20, 65.0).then(setGridStatus).catch(console.error);
  }, []);

  const handleRunEvaluation = async () => {
    setLoading(true);
    try {
      const res = await evaluateGridDemandResponse(15, 70.0);
      setGridStatus(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const getTierColor = (tier: string) => {
    if (tier === "SOLAR_SURPLUS") return { text: "#38bdf8", bg: "rgba(56, 189, 248, 0.15)", border: "#0284c7" };
    if (tier === "OFF_PEAK") return { text: "#4ade80", bg: "rgba(74, 222, 128, 0.15)", border: "#16a34a" };
    if (tier === "SHOULDER") return { text: "#facc15", bg: "rgba(250, 204, 21, 0.15)", border: "#ca8a04" };
    return { text: "#f87171", bg: "rgba(248, 113, 113, 0.15)", border: "#dc2626" };
  };

  return (
    <div className="card" style={{ padding: "1.25rem", borderRadius: "1rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
          <div style={{ background: "rgba(234, 179, 8, 0.15)", padding: "0.5rem", borderRadius: "0.6rem", color: "#facc15" }}>
            <Zap size={20} />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700 }}>Smart Grid Dynamic Tariff Optimization</h3>
              {gridStatus?.solar_surplus_active && (
                <span className="badge" style={{ background: "rgba(56, 189, 248, 0.2)", color: "#38bdf8" }}>
                  <Sun size={12} style={{ marginRight: "0.2rem" }} /> Solar Surplus Active
                </span>
              )}
            </div>
            <p style={{ margin: 0, fontSize: "0.78rem", color: "var(--text-muted)" }}>
              Pre-emptive air scrubbing scheduled during off-peak and negative solar surplus wholesale tariff windows
            </p>
          </div>
        </div>

        <button
          className="btn btn-secondary"
          onClick={handleRunEvaluation}
          disabled={loading}
          style={{ fontSize: "0.8rem", padding: "0.4rem 0.85rem" }}
        >
          {loading ? "Optimizing..." : "Evaluate Demand Response"}
        </button>
      </div>

      {gridStatus && (
        <div>
          {/* Main Stats */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "0.75rem", marginBottom: "1rem" }}>
            {/* Tariff Tier */}
            <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)", borderRadius: "0.75rem", padding: "0.85rem" }}>
              <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Current Grid Tariff Tier</div>
              <div style={{ display: "flex", alignItems: "baseline", gap: "0.4rem", marginTop: "0.2rem" }}>
                <span style={{ fontSize: "1.3rem", fontWeight: 800, color: getTierColor(gridStatus.current_tariff_tier).text }}>
                  {gridStatus.current_tariff_tier}
                </span>
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                {gridStatus.current_rate_cents_per_kwh.toFixed(1)} ¢ / kWh
              </div>
            </div>

            {/* Preemptive Scrubbing */}
            <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)", borderRadius: "0.75rem", padding: "0.85rem" }}>
              <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Pre-Emptive Scrubbing</div>
              <div style={{ display: "flex", alignItems: "baseline", gap: "0.4rem", marginTop: "0.2rem" }}>
                <span style={{ fontSize: "1.3rem", fontWeight: 800, color: gridStatus.preemptive_scrubbing_engaged ? "#4ade80" : "#94a3b8" }}>
                  {gridStatus.preemptive_scrubbing_engaged ? "ENGAGED" : "STANDBY"}
                </span>
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Target CADR: {gridStatus.calculated_cadr_cfm} CFM
              </div>
            </div>

            {/* Savings */}
            <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)", borderRadius: "0.75rem", padding: "0.85rem" }}>
              <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Energy Cost Savings</div>
              <div style={{ display: "flex", alignItems: "baseline", gap: "0.4rem", marginTop: "0.2rem" }}>
                <span style={{ fontSize: "1.3rem", fontWeight: 800, color: "#22c55e" }}>
                  {gridStatus.total_savings_pct}%
                </span>
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                vs Reactive Peak-Hour Scrubbing
              </div>
            </div>

            {/* Decay Constant k */}
            <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)", borderRadius: "0.75rem", padding: "0.85rem" }}>
              <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Fitted Removal Constant (k)</div>
              <div style={{ display: "flex", alignItems: "baseline", gap: "0.4rem", marginTop: "0.2rem" }}>
                <span style={{ fontSize: "1.3rem", fontWeight: 800, color: "#a855f7" }}>
                  {gridStatus.cadr_decay_constant_k || 0.085} min⁻¹
                </span>
              </div>
              <div style={{ fontSize: "0.75rem", color: "#c084fc" }}>
                C(t) = C_amb + (C₀ - C_amb)e⁻ᵏᵗ
              </div>
            </div>
          </div>

          {/* Workflow Sequence Diagram Box */}
          <div style={{ background: "rgba(0,0,0,0.25)", border: "1px solid var(--border)", borderRadius: "0.75rem", padding: "0.85rem" }}>
            <div style={{ fontSize: "0.78rem", fontWeight: 600, color: "#94a3b8", marginBottom: "0.5rem" }}>
              Grid-Aware Automation Loop: Forecast Trigger → Tariff Window → CADR Exponential Decay Fit
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "0.5rem", fontSize: "0.75rem" }}>
              <div style={{ background: "rgba(255,255,255,0.03)", padding: "0.5rem", borderRadius: "0.4rem" }}>
                <span style={{ color: "#facc15", fontWeight: 600 }}>1. Predictive Trigger</span>
                <p style={{ margin: "0.2rem 0 0 0", color: "#cbd5e1" }}>
                  PM2.5 forecasted to spike to 65 µg/m³ in {gridStatus.forecasted_pm25_spike_mins} mins.
                </p>
              </div>
              <div style={{ background: "rgba(255,255,255,0.03)", padding: "0.5rem", borderRadius: "0.4rem" }}>
                <span style={{ color: "#38bdf8", fontWeight: 600 }}>2. Dynamic Tariff Evaluator</span>
                <p style={{ margin: "0.2rem 0 0 0", color: "#cbd5e1" }}>
                  Grid rate is currently {gridStatus.current_tariff_tier} ({gridStatus.current_rate_cents_per_kwh}¢/kWh).
                </p>
              </div>
              <div style={{ background: "rgba(255,255,255,0.03)", padding: "0.5rem", borderRadius: "0.4rem" }}>
                <span style={{ color: "#4ade80", fontWeight: 600 }}>3. Pre-Emptive Scrubbing</span>
                <p style={{ margin: "0.2rem 0 0 0", color: "#cbd5e1" }}>
                  Run purifiers at Max before peak rate window to build clean air buffer.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
