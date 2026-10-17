import React, { useState, useEffect } from "react";
import {
  Heart,
  Activity,
  Droplet,
  Wind,
  Watch,
  ShieldAlert,
  Sparkles,
  RefreshCw,
  TrendingUp
} from "lucide-react";
import type { DynamicIntakeResponse } from "../types";
import { fetchDynamicInhalationIntake, syncWearable } from "../api";

export const BiometricWearableCard: React.FC = () => {
  const [source, setSource] = useState<string>("APPLE_HEALTHKIT");
  const [hr, setHr] = useState<number>(78);
  const [hrv, setHrv] = useState<number>(58);
  const [spo2, setSpo2] = useState<number>(98.5);
  const [rr, setRr] = useState<number>(15);
  const [intakeData, setIntakeData] = useState<DynamicIntakeResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchIntake = async () => {
    try {
      const res = await fetchDynamicInhalationIntake("default_user");
      setIntakeData(res);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchIntake();
  }, []);

  const handleSync = async () => {
    setLoading(true);
    try {
      await syncWearable({
        user_id: "default_user",
        source,
        heart_rate_bpm: hr,
        hrv_ms: hrv,
        spo2_pct: spo2,
        respiratory_rate_bpm: rr
      });
      await fetchIntake();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const getStrainBadge = (strain?: string) => {
    if (strain === "BRONCHIAL_WARNING") return { color: "#f43f5e", bg: "rgba(244, 63, 94, 0.15)", text: "Bronchial Warning" };
    if (strain === "HIGH_STRAIN") return { color: "#f97316", bg: "rgba(249, 115, 22, 0.15)", text: "High Strain" };
    if (strain === "MILD_STRAIN") return { color: "#eab308", bg: "rgba(234, 179, 8, 0.15)", text: "Mild Activity Strain" };
    return { color: "#22c55e", bg: "rgba(34, 197, 94, 0.15)", text: "Resting / Nominal" };
  };

  const strainBadge = getStrainBadge(intakeData?.physiological_strain_index);

  return (
    <div className="card" style={{ padding: "1.25rem", borderRadius: "1rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
          <div style={{ background: "rgba(244, 63, 94, 0.15)", padding: "0.5rem", borderRadius: "0.6rem", color: "#f43f5e" }}>
            <Watch size={20} />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700 }}>Biometric Wearable Health Fusion</h3>
              <span className="badge" style={{ background: strainBadge.bg, color: strainBadge.color }}>
                {strainBadge.text}
              </span>
            </div>
            <p style={{ margin: 0, fontSize: "0.78rem", color: "var(--text-muted)" }}>
              Continuous minute ventilation scaling: I_pollutant = Σ C_i · V_E(HeartRate) · Δt_i
            </p>
          </div>
        </div>

        {/* Source Switcher */}
        <div style={{ display: "flex", gap: "0.3rem" }}>
          {["APPLE_HEALTHKIT", "GARMIN", "WHOOP"].map((s) => (
            <button
              key={s}
              onClick={() => setSource(s)}
              style={{
                fontSize: "0.72rem",
                padding: "0.3rem 0.6rem",
                borderRadius: "0.4rem",
                border: "1px solid var(--border)",
                background: source === s ? "rgba(244, 63, 94, 0.2)" : "rgba(255,255,255,0.03)",
                color: source === s ? "#fda4af" : "var(--text-muted)",
                cursor: "pointer"
              }}
            >
              {s.replace("_", " ")}
            </button>
          ))}
        </div>
      </div>

      {/* 4 Biometric Tiles */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: "0.75rem", marginBottom: "1rem" }}>
        {/* Heart Rate */}
        <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)", borderRadius: "0.75rem", padding: "0.75rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", color: "var(--text-muted)", fontSize: "0.72rem" }}>
            <span>Heart Rate</span>
            <Heart size={14} color="#f43f5e" />
          </div>
          <div style={{ fontSize: "1.3rem", fontWeight: 800, color: "#f43f5e", marginTop: "0.2rem" }}>
            {hr} <span style={{ fontSize: "0.75rem", fontWeight: 500, color: "var(--text-muted)" }}>bpm</span>
          </div>
          <input
            type="range"
            min="50"
            max="160"
            value={hr}
            onChange={(e) => setHr(parseInt(e.target.value))}
            style={{ width: "100%", marginTop: "0.3rem" }}
          />
        </div>

        {/* HRV */}
        <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)", borderRadius: "0.75rem", padding: "0.75rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", color: "var(--text-muted)", fontSize: "0.72rem" }}>
            <span>HRV (rMSSD)</span>
            <Activity size={14} color="#a855f7" />
          </div>
          <div style={{ fontSize: "1.3rem", fontWeight: 800, color: "#c084fc", marginTop: "0.2rem" }}>
            {hrv} <span style={{ fontSize: "0.75rem", fontWeight: 500, color: "var(--text-muted)" }}>ms</span>
          </div>
          <div style={{ fontSize: "0.68rem", color: "var(--text-muted)", marginTop: "0.4rem" }}>
            Autonomic Balance
          </div>
        </div>

        {/* SpO2 */}
        <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)", borderRadius: "0.75rem", padding: "0.75rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", color: "var(--text-muted)", fontSize: "0.72rem" }}>
            <span>Blood Oxygen</span>
            <Droplet size={14} color="#38bdf8" />
          </div>
          <div style={{ fontSize: "1.3rem", fontWeight: 800, color: "#38bdf8", marginTop: "0.2rem" }}>
            {spo2} <span style={{ fontSize: "0.75rem", fontWeight: 500, color: "var(--text-muted)" }}>%</span>
          </div>
          <div style={{ fontSize: "0.68rem", color: "var(--text-muted)", marginTop: "0.4rem" }}>
            Arterial Saturation
          </div>
        </div>

        {/* Respiratory Rate */}
        <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)", borderRadius: "0.75rem", padding: "0.75rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", color: "var(--text-muted)", fontSize: "0.72rem" }}>
            <span>Respiration</span>
            <Wind size={14} color="#22c55e" />
          </div>
          <div style={{ fontSize: "1.3rem", fontWeight: 800, color: "#4ade80", marginTop: "0.2rem" }}>
            {rr} <span style={{ fontSize: "0.75rem", fontWeight: 500, color: "var(--text-muted)" }}>br/m</span>
          </div>
          <div style={{ fontSize: "0.68rem", color: "var(--text-muted)", marginTop: "0.4rem" }}>
            Airway Flux Rate
          </div>
        </div>
      </div>

      {/* Dynamic V_E & Dosage Impact Box */}
      {intakeData && (
        <div style={{ background: "rgba(0,0,0,0.25)", border: "1px solid var(--border)", borderRadius: "0.75rem", padding: "0.85rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ fontSize: "0.78rem", color: "#94a3b8" }}>
                Dynamic Minute Ventilation Rate <strong style={{ color: "#f8fafc" }}>V_E(HR): {intakeData.dynamic_ve_lpm} L/min</strong>
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.15rem" }}>
                Resting Baseline: {intakeData.baseline_resting_hr} bpm (12.0 L/min)
              </div>
            </div>

            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: "0.78rem", color: "#fca5a5" }}>
                Heart Rate Exertion Impact: <strong>+{intakeData.excess_intake_due_to_hr_pct}% Inhaled Mass</strong>
              </div>
              <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                Hourly Dose: {intakeData.cumulative_intake_pm25_ug} µg PM2.5
              </div>
            </div>

            <button
              className="btn btn-secondary"
              onClick={handleSync}
              disabled={loading}
              style={{ padding: "0.4rem 0.8rem", fontSize: "0.78rem" }}
            >
              <RefreshCw size={12} className={loading ? "spin" : ""} style={{ marginRight: "0.3rem" }} />
              Sync Biometrics
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
