import React, { useState } from "react";
import { RemediationAction } from "../types";
import { Sparkles, Check, Clock, TrendingDown, RefreshCw } from "lucide-react";

interface ActionTrackerProps {
  activeAction: RemediationAction | null;
  actionHistory: RemediationAction[];
  onLogAction: (actionType: string, description: string) => Promise<void>;
  onResolveAction: (actionId: number) => Promise<void>;
  isOpenModal: boolean;
  onCloseModal: () => void;
}

export const ActionTracker: React.FC<ActionTrackerProps> = ({
  activeAction,
  actionHistory,
  onLogAction,
  onResolveAction,
  isOpenModal,
  onCloseModal,
}) => {
  const [actionType, setActionType] = useState("OPEN_WINDOW");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onLogAction(actionType, description || `Initiated ${actionType.replace("_", " ").toLowerCase()}`);
      setDescription("");
      onCloseModal();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      {/* Active Remediation Banner in Dashboard */}
      {activeAction && (
        <div className="glass-panel" style={{
          padding: "18px 24px",
          borderRadius: "16px",
          background: "linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(99, 102, 241, 0.12) 100%)",
          border: "1px solid rgba(6, 182, 212, 0.35)",
          marginBottom: "16px"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
            
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <div style={{
                background: "rgba(6, 182, 212, 0.25)",
                padding: "10px",
                borderRadius: "10px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center"
              }}>
                <RefreshCw size={20} color="#38bdf8" className="spin-slow" />
              </div>

              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ fontSize: "11px", fontWeight: "700", textTransform: "uppercase", color: "#38bdf8" }}>
                    Active Closed-Loop Remediation Tracker (FR-6.2)
                  </span>
                  <span className="glass-pill" style={{ fontSize: "10px", color: "#e2e8f0" }}>
                    In Progress
                  </span>
                </div>
                <h4 style={{ fontSize: "16px", fontWeight: "700", color: "#ffffff", marginTop: "2px" }}>
                  {activeAction.description}
                </h4>
              </div>
            </div>

            {/* Metrics: Initial -> Current -> Target */}
            <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
              <div>
                <span style={{ fontSize: "10px", color: "var(--text-muted)", display: "block" }}>Initial AQI</span>
                <span className="mono-num" style={{ fontSize: "18px", fontWeight: "700", color: "#f87171" }}>
                  {activeAction.initial_aqi}
                </span>
              </div>

              <div>
                <span style={{ fontSize: "10px", color: "var(--text-muted)", display: "block" }}>Current</span>
                <span className="mono-num" style={{ fontSize: "18px", fontWeight: "700", color: "#38bdf8" }}>
                  {activeAction.current_aqi}
                </span>
              </div>

              <div>
                <span style={{ fontSize: "10px", color: "var(--text-muted)", display: "block" }}>Target Goal</span>
                <span className="mono-num" style={{ fontSize: "18px", fontWeight: "700", color: "#34d399" }}>
                  {activeAction.target_aqi}
                </span>
              </div>

              <button
                onClick={() => onResolveAction(activeAction.id)}
                className="btn-primary"
                style={{ fontSize: "12px", padding: "7px 14px" }}
              >
                <Check size={14} />
                <span>Mark Resolved</span>
              </button>
            </div>

          </div>
        </div>
      )}

      {/* Modal for logging remediation */}
      {isOpenModal && (
        <div className="modal-overlay" onClick={onCloseModal}>
          <div
            className="glass-panel"
            style={{ width: "100%", maxWidth: "460px", padding: "24px", borderRadius: "18px" }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
              <Sparkles size={22} color="#38bdf8" />
              <h3 style={{ fontSize: "18px", fontWeight: "700", color: "#ffffff" }}>
                Log Remediation Action
              </h3>
            </div>

            <p style={{ fontSize: "13px", color: "var(--text-muted)", marginBottom: "16px" }}>
              Track how effectively your physical intervention restores optimal room air quality.
            </p>

            <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div>
                <label style={{ fontSize: "12px", color: "var(--text-muted)", display: "block", marginBottom: "6px" }}>
                  Intervention Category:
                </label>
                <select
                  value={actionType}
                  onChange={(e) => setActionType(e.target.value)}
                  style={{
                    width: "100%",
                    background: "rgba(15, 23, 42, 0.9)",
                    border: "1px solid rgba(255, 255, 255, 0.15)",
                    borderRadius: "10px",
                    padding: "10px 12px",
                    color: "#ffffff",
                    fontSize: "13px",
                    outline: "none"
                  }}
                >
                  <option value="OPEN_WINDOW">Open Windows (Fresh Air Exchange)</option>
                  <option value="HEPA_PURIFIER">Activate Standalone HEPA Purifier</option>
                  <option value="EXHAUST_HOOD">Turn On Range Hood Exhaust</option>
                  <option value="HVAC_FRESH_AIR">Set HVAC Damper to 100% Outdoor Air</option>
                  <option value="REMOVE_SOURCE">Remove Chemical / Odor Source</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: "12px", color: "var(--text-muted)", display: "block", marginBottom: "6px" }}>
                  Description / Note:
                </label>
                <input
                  type="text"
                  placeholder="e.g., Opened both bedroom windows for cross-breeze"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  style={{
                    width: "100%",
                    background: "rgba(15, 23, 42, 0.9)",
                    border: "1px solid rgba(255, 255, 255, 0.15)",
                    borderRadius: "10px",
                    padding: "10px 12px",
                    color: "#ffffff",
                    fontSize: "13px",
                    outline: "none"
                  }}
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "10px" }}>
                <button type="button" onClick={onCloseModal} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" disabled={submitting} className="btn-primary">
                  {submitting ? "Logging..." : "Start Tracking Recovery"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
};
