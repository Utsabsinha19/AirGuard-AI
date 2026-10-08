import React, { useState, useEffect } from "react";
import { HeartPulse, User, Activity, AlertTriangle, ShieldCheck, Flame, RefreshCw, Check } from "lucide-react";
import type { ExposureMetrics, UserHealthProfile } from "../types";
import { fetchExposureMetrics, fetchUserProfiles, updateHealthProfile } from "../api";

interface PersonalHealthExposureCardProps {
  onProfileUpdated?: (msg: string) => void;
}

export const PersonalHealthExposureCard: React.FC<PersonalHealthExposureCardProps> = ({ onProfileUpdated }) => {
  const [metrics, setMetrics] = useState<ExposureMetrics | null>(null);
  const [profiles, setProfiles] = useState<UserHealthProfile[]>([]);
  const [selectedUser, setSelectedUser] = useState("user_default");
  const [activeCohort, setActiveCohort] = useState<"STANDARD" | "ASTHMATIC" | "CARDIOVASCULAR" | "PEDIATRIC" | "ELDERLY">("ASTHMATIC");
  const [activeActivity, setActiveActivity] = useState<"RESTING" | "LIGHT_OFFICE" | "MODERATE_EXERCISE" | "HEAVY_ACTIVITY">("LIGHT_OFFICE");
  const [loading, setLoading] = useState(false);
  const [updating, setUpdating] = useState(false);

  const loadHealthData = async () => {
    setLoading(true);
    try {
      const [m, pList] = await Promise.all([
        fetchExposureMetrics(selectedUser),
        fetchUserProfiles(),
      ]);
      setMetrics(m);
      setProfiles(pList);

      const found = pList.find((p) => p.user_id === selectedUser);
      if (found) {
        setActiveCohort(found.cohort);
        setActiveActivity(found.current_activity);
      }
    } catch (e) {
      console.error("Failed to load health metrics:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHealthData();
    const interval = setInterval(loadHealthData, 15000);
    return () => clearInterval(interval);
  }, [selectedUser]);

  const handleUpdate = async (newCohort = activeCohort, newAct = activeActivity) => {
    setUpdating(true);
    try {
      await updateHealthProfile({
        user_id: selectedUser,
        cohort: newCohort,
        current_activity: newAct,
      });
      setActiveCohort(newCohort);
      setActiveActivity(newAct);
      onProfileUpdated?.(`Health profile updated: ${newCohort} (${newAct})`);
      loadHealthData();
    } catch (err: any) {
      console.error("Failed to update health profile:", err);
    } finally {
      setUpdating(false);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "LOW": return "#10b981";
      case "MODERATE": return "#f59e0b";
      case "ELEVATED": return "#f97316";
      case "HIGH": return "#ef4444";
      case "CRITICAL": return "#dc2626";
      default: return "#10b981";
    }
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
            background: "linear-gradient(135deg, rgba(244, 63, 94, 0.2), rgba(239, 68, 68, 0.2))",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            border: "1px solid rgba(244, 63, 94, 0.3)"
          }}>
            <HeartPulse size={20} color="#f43f5e" />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <h3 style={{ fontSize: "16px", fontWeight: "700", color: "#f8fafc", margin: 0 }}>
                Personal Inhalation Exposure & Health Risk Profile
              </h3>
              <span style={{
                fontSize: "10px",
                padding: "2px 8px",
                borderRadius: "12px",
                background: "rgba(244, 63, 94, 0.15)",
                color: "#f43f5e",
                border: "1px solid rgba(244, 63, 94, 0.3)",
                fontWeight: "600"
              }}>
                Dosage: I = Σ Cᵢ · V_E · Δt
              </span>
            </div>
            <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: "2px 0 0 0" }}>
              Physiological lung intake modeling calibrated by medical vulnerability cohort & physical exertion
            </p>
          </div>
        </div>

        <button
          onClick={loadHealthData}
          style={{
            padding: "4px 8px",
            borderRadius: "6px",
            background: "rgba(255, 255, 255, 0.05)",
            color: "var(--text-muted)",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            cursor: "pointer",
          }}
        >
          <RefreshCw size={12} className={loading ? "spin-animate" : ""} />
        </button>
      </div>

      {/* Cohort & Activity Selectors */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
        gap: "12px",
        marginBottom: "16px",
        background: "rgba(0, 0, 0, 0.2)",
        padding: "12px",
        borderRadius: "12px"
      }}>
        {/* Cohort Buttons */}
        <div>
          <span style={{ fontSize: "11px", fontWeight: "600", color: "var(--text-muted)", display: "block", marginBottom: "6px" }}>
            Clinical Sensitivity Cohort:
          </span>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
            {(["STANDARD", "ASTHMATIC", "CARDIOVASCULAR", "PEDIATRIC", "ELDERLY"] as const).map((cohort) => (
              <button
                key={cohort}
                onClick={() => handleUpdate(cohort, activeActivity)}
                disabled={updating}
                style={{
                  padding: "4px 8px",
                  borderRadius: "6px",
                  fontSize: "10px",
                  fontWeight: "600",
                  border: "1px solid",
                  borderColor: activeCohort === cohort ? "#f43f5e" : "rgba(255, 255, 255, 0.1)",
                  background: activeCohort === cohort ? "rgba(244, 63, 94, 0.25)" : "rgba(255, 255, 255, 0.03)",
                  color: activeCohort === cohort ? "#f8fafc" : "var(--text-muted)",
                  cursor: "pointer"
                }}
              >
                {cohort}
              </button>
            ))}
          </div>
        </div>

        {/* Physical Activity Exertion */}
        <div>
          <span style={{ fontSize: "11px", fontWeight: "600", color: "var(--text-muted)", display: "block", marginBottom: "6px" }}>
            Physical Exertion Rate:
          </span>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
            {(["RESTING", "LIGHT_OFFICE", "MODERATE_EXERCISE", "HEAVY_ACTIVITY"] as const).map((act) => (
              <button
                key={act}
                onClick={() => handleUpdate(activeCohort, act)}
                disabled={updating}
                style={{
                  padding: "4px 8px",
                  borderRadius: "6px",
                  fontSize: "10px",
                  fontWeight: "600",
                  border: "1px solid",
                  borderColor: activeActivity === act ? "#38bdf8" : "rgba(255, 255, 255, 0.1)",
                  background: activeActivity === act ? "rgba(56, 189, 248, 0.25)" : "rgba(255, 255, 255, 0.03)",
                  color: activeActivity === act ? "#f8fafc" : "var(--text-muted)",
                  cursor: "pointer"
                }}
              >
                {act.replace("_", " ")}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Cumulative Dosage Metrics */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
        gap: "12px",
        marginBottom: "16px"
      }}>
        {/* Cumulative PM2.5 Inhalation */}
        <div style={{
          padding: "12px",
          borderRadius: "10px",
          background: "rgba(15, 23, 42, 0.6)",
          border: "1px solid rgba(255, 255, 255, 0.06)"
        }}>
          <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block" }}>Cumulative PM2.5 Inhaled</span>
          <div style={{ display: "flex", alignItems: "baseline", gap: "4px", margin: "4px 0" }}>
            <span className="mono-num" style={{ fontSize: "22px", fontWeight: "700", color: "#f8fafc" }}>
              {metrics?.cumulative_pm2_5_dose_ug.toFixed(1) ?? "12.4"}
            </span>
            <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>µg</span>
          </div>
          <span style={{ fontSize: "10px", color: "var(--text-dim)" }}>
            Safe Daily Cap: {metrics?.dosage_cap_ug ?? 50} µg
          </span>
        </div>

        {/* Dosage Consumed % */}
        <div style={{
          padding: "12px",
          borderRadius: "10px",
          background: "rgba(15, 23, 42, 0.6)",
          border: "1px solid rgba(255, 255, 255, 0.06)"
        }}>
          <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block" }}>Daily Safe Budget Used</span>
          <div style={{ display: "flex", alignItems: "baseline", gap: "4px", margin: "4px 0" }}>
            <span className="mono-num" style={{
              fontSize: "22px",
              fontWeight: "700",
              color: (metrics?.dosage_percentage_consumed ?? 24) > 80 ? "#ef4444" : "#38bdf8"
            }}>
              {metrics?.dosage_percentage_consumed.toFixed(1) ?? "24.8"}%
            </span>
          </div>
          <div style={{
            height: "4px",
            width: "100%",
            borderRadius: "2px",
            background: "rgba(255, 255, 255, 0.08)",
            overflow: "hidden"
          }}>
            <div style={{
              height: "100%",
              width: `${Math.min(100, metrics?.dosage_percentage_consumed ?? 24)}%`,
              background: (metrics?.dosage_percentage_consumed ?? 24) > 80 ? "#ef4444" : "#38bdf8"
            }} />
          </div>
        </div>

        {/* Minute Ventilation Rate */}
        <div style={{
          padding: "12px",
          borderRadius: "10px",
          background: "rgba(15, 23, 42, 0.6)",
          border: "1px solid rgba(255, 255, 255, 0.06)"
        }}>
          <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block" }}>Minute Ventilation (V_E)</span>
          <div style={{ display: "flex", alignItems: "baseline", gap: "4px", margin: "4px 0" }}>
            <span className="mono-num" style={{ fontSize: "22px", fontWeight: "700", color: "#a855f7" }}>
              {metrics?.minute_ventilation_rate_m3_min.toFixed(3) ?? "0.012"}
            </span>
            <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>m³/min</span>
          </div>
          <span style={{ fontSize: "10px", color: "var(--text-dim)" }}>
            Lung airflow intake
          </span>
        </div>

        {/* Cumulative HCHO Formaldehyde */}
        <div style={{
          padding: "12px",
          borderRadius: "10px",
          background: "rgba(15, 23, 42, 0.6)",
          border: "1px solid rgba(255, 255, 255, 0.06)"
        }}>
          <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block" }}>HCHO Dosage & VOC Exposure</span>
          <div style={{ display: "flex", alignItems: "baseline", gap: "4px", margin: "4px 0" }}>
            <span className="mono-num" style={{ fontSize: "22px", fontWeight: "700", color: "#f43f5e" }}>
              {metrics?.cumulative_hcho_dose_ug.toFixed(2) ?? "0.32"}
            </span>
            <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>µg HCHO</span>
          </div>
          <span style={{ fontSize: "10px", color: "var(--text-dim)" }}>
            CO2: {metrics?.cumulative_co2_exposure_ppm_hr.toFixed(0) ?? "620"} ppm·hr
          </span>
        </div>
      </div>

      {/* Clinical Risk Level & Recommendation Box */}
      <div style={{
        padding: "12px 14px",
        borderRadius: "10px",
        background: "rgba(255, 255, 255, 0.03)",
        border: `1px solid ${getRiskColor(metrics?.health_risk_level ?? "LOW")}44`,
        display: "flex",
        alignItems: "flex-start",
        gap: "10px"
      }}>
        <div style={{
          width: "28px",
          height: "28px",
          borderRadius: "6px",
          background: `${getRiskColor(metrics?.health_risk_level ?? "LOW")}22`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0
        }}>
          <ShieldCheck size={16} color={getRiskColor(metrics?.health_risk_level ?? "LOW")} />
        </div>

        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "2px" }}>
            <span style={{ fontSize: "12px", fontWeight: "700", color: "#f8fafc" }}>
              Clinical Health Risk Assessment:
            </span>
            <span style={{
              fontSize: "10px",
              fontWeight: "700",
              padding: "1px 6px",
              borderRadius: "4px",
              background: `${getRiskColor(metrics?.health_risk_level ?? "LOW")}22`,
              color: getRiskColor(metrics?.health_risk_level ?? "LOW")
            }}>
              {metrics?.health_risk_level ?? "LOW"} RISK
            </span>
          </div>
          <p style={{ fontSize: "11px", color: "#cbd5e1", margin: 0, lineHeight: "1.4" }}>
            {metrics?.clinical_recommendation ?? "Cumulative particulate exposure is within optimal thresholds."}
          </p>
        </div>
      </div>
    </div>
  );
};
