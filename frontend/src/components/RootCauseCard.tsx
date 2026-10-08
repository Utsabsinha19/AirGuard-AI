import React from "react";
import { AnomalyDiagnosis } from "../types";
import { HelpCircle, AlertOctagon, CheckCircle2, Lightbulb, ArrowRight } from "lucide-react";

interface RootCauseCardProps {
  diagnosis: AnomalyDiagnosis | null;
  onTakeAction?: () => void;
}

export const RootCauseCard: React.FC<RootCauseCardProps> = ({ diagnosis, onTakeAction }) => {
  const isAnomaly = diagnosis?.is_anomaly ?? false;
  const severity = diagnosis?.severity ?? "NORMAL";
  const title = diagnosis?.root_cause_title ?? "Atmosphere Optimal & Nominal";
  const description = diagnosis?.description ?? "All environmental sensors are within safe baseline limits. No pollution sources detected.";
  const recommendation = diagnosis?.recommendation ?? "Maintain normal room use; no action required.";
  const contributions = diagnosis?.sensor_contributions ?? { "PM2.5": 10, "CO2": 15, "VOC": 12 };

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case "CRITICAL":
        return { label: "CRITICAL HAZARD", bg: "rgba(239, 68, 68, 0.2)", border: "#ef4444", text: "#f87171" };
      case "HIGH":
        return { label: "HIGH ANOMALY", bg: "rgba(249, 115, 22, 0.2)", border: "#f97316", text: "#fb923c" };
      case "MEDIUM":
        return { label: "MODERATE SPIKE", bg: "rgba(245, 158, 11, 0.2)", border: "#f59e0b", text: "#fbbf24" };
      case "LOW":
        return { label: "MILD DRIFT", bg: "rgba(56, 189, 248, 0.2)", border: "#38bdf8", text: "#7dd3fc" };
      default:
        return { label: "STABLE BASELINE", bg: "rgba(16, 185, 129, 0.2)", border: "#10b981", text: "#34d399" };
    }
  };

  const badge = getSeverityBadge(severity);

  return (
    <div className="glass-panel" style={{ padding: "24px", borderRadius: "18px", display: "flex", flexDirection: "column", gap: "16px" }}>
      
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "10px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          {isAnomaly ? (
            <AlertOctagon size={22} color={badge.border} />
          ) : (
            <CheckCircle2 size={22} color="#10b981" />
          )}
          <div>
            <h3 style={{ fontSize: "17px", fontWeight: "700", color: "#f8fafc" }}>
              Root-Cause & Anomaly Intelligence (FR-4.3)
            </h3>
            <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
              Multi-sensor cross-correlation diagnostic engine
            </span>
          </div>
        </div>

        <div style={{
          padding: "5px 12px",
          borderRadius: "9999px",
          background: badge.bg,
          border: `1px solid ${badge.border}`,
          display: "flex",
          alignItems: "center",
          gap: "6px"
        }}>
          <div style={{ width: "6px", height: "6px", borderRadius: "50%", background: badge.border }} />
          <span style={{ fontSize: "11px", fontWeight: "700", color: badge.text }}>
            {badge.label}
          </span>
        </div>
      </div>

      {/* Target Question 1: "Is this unusual?" & "Why is it getting worse?" */}
      <div style={{
        background: "rgba(255, 255, 255, 0.03)",
        border: "1px solid rgba(255, 255, 255, 0.06)",
        borderRadius: "14px",
        padding: "16px"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "6px" }}>
          <span style={{ fontSize: "11px", textTransform: "uppercase", letterSpacing: "0.06em", color: "#38bdf8", fontWeight: "700" }}>
            Diagnosed Source:
          </span>
        </div>
        <h4 style={{ fontSize: "16px", fontWeight: "700", color: "#ffffff", marginBottom: "6px" }}>
          {title}
        </h4>
        <p style={{ fontSize: "13px", color: "#cbd5e1", lineHeight: "1.5" }}>
          {description}
        </p>

        {/* Multi-Sensor Contribution attribution bars */}
        {isAnomaly && (
          <div style={{ marginTop: "14px" }}>
            <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600", display: "block", marginBottom: "8px" }}>
              Cross-Sensor Anomaly Attribution:
            </span>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "10px" }}>
              {Object.entries(contributions).map(([sensor, val]) => (
                <div key={sensor} style={{ background: "rgba(0, 0, 0, 0.2)", padding: "8px", borderRadius: "8px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", marginBottom: "4px" }}>
                    <span style={{ color: "#94a3b8" }}>{sensor}</span>
                    <span style={{ color: "#f8fafc", fontWeight: "700" }}>{Math.round(val)}%</span>
                  </div>
                  <div style={{ height: "4px", background: "rgba(255, 255, 255, 0.1)", borderRadius: "2px", overflow: "hidden" }}>
                    <div style={{
                      height: "100%",
                      width: `${Math.min(100, val)}%`,
                      background: val > 60 ? "#ef4444" : val > 30 ? "#f59e0b" : "#38bdf8",
                      borderRadius: "2px"
                    }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Target Question 2: "What should I do?" (Actionable Guidance FR-5.3) */}
      <div style={{
        background: "rgba(99, 102, 241, 0.08)",
        border: "1px solid rgba(99, 102, 241, 0.25)",
        borderRadius: "14px",
        padding: "16px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: "12px"
      }}>
        <div style={{ display: "flex", alignItems: "flex-start", gap: "10px", flex: 1, minWidth: "240px" }}>
          <div style={{
            background: "rgba(99, 102, 241, 0.2)",
            borderRadius: "8px",
            padding: "8px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center"
          }}>
            <Lightbulb size={20} color="#a5b4fc" />
          </div>
          <div>
            <span style={{ fontSize: "11px", fontWeight: "700", color: "#a5b4fc", textTransform: "uppercase" }}>
              Actionable Recommendation (FR-5.3)
            </span>
            <p style={{ fontSize: "13px", color: "#e0e7ff", marginTop: "2px", lineHeight: "1.4" }}>
              {recommendation}
            </p>
          </div>
        </div>

        {onTakeAction && (
          <button
            onClick={onTakeAction}
            className="btn-primary"
            style={{ fontSize: "12px", padding: "8px 14px" }}
          >
            <span>Log Remediation</span>
            <ArrowRight size={14} />
          </button>
        )}
      </div>

    </div>
  );
};
