import React from "react";
import type { AlertItem } from "../types";
import { Bell, X, Check, AlertOctagon, AlertTriangle, Sparkles } from "lucide-react";

interface AlertCenterProps {
  alerts: AlertItem[];
  isOpen: boolean;
  onClose: () => void;
  onAcknowledge: (id: number) => void;
  onAcknowledgeAll: () => void;
  onConvertToAction?: (alertId: number) => void;
}

export const AlertCenter: React.FC<AlertCenterProps> = ({
  alerts,
  isOpen,
  onClose,
  onAcknowledge,
  onAcknowledgeAll,
  onConvertToAction,
}) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="glass-panel"
        style={{
          width: "100%",
          maxWidth: "540px",
          maxHeight: "85vh",
          padding: "24px",
          borderRadius: "20px",
          display: "flex",
          flexDirection: "column",
          gap: "16px"
        }}
        onClick={(e) => e.stopPropagation()}
      >
        
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <Bell size={20} color="#f43f5e" />
            <h3 style={{ fontSize: "18px", fontWeight: "700", color: "#ffffff" }}>
              Alert & Remediation Center (Section 2.3)
            </h3>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            {alerts.some((a) => !a.acknowledged) && (
              <button
                onClick={onAcknowledgeAll}
                className="btn-secondary"
                style={{ fontSize: "11px", padding: "5px 10px" }}
              >
                Ack All
              </button>
            )}
            <button
              onClick={onClose}
              style={{
                background: "transparent",
                border: "none",
                color: "var(--text-muted)",
                cursor: "pointer",
                padding: "4px"
              }}
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Alert List */}
        <div style={{ overflowY: "auto", display: "flex", flexDirection: "column", gap: "10px", paddingRight: "4px" }}>
          {alerts.length === 0 ? (
            <div style={{ textAlign: "center", padding: "40px 0", color: "var(--text-muted)" }}>
              <p style={{ fontSize: "14px" }}>No active alerts. Atmosphere is nominal.</p>
            </div>
          ) : (
            alerts.map((alert) => {
              const isCrit = alert.level === "CRITICAL";
              const border = isCrit ? "#ef4444" : "#f59e0b";

              return (
                <div
                  key={alert.id}
                  style={{
                    background: alert.acknowledged ? "rgba(255, 255, 255, 0.02)" : "rgba(255, 255, 255, 0.06)",
                    border: `1px solid ${alert.acknowledged ? "rgba(255, 255, 255, 0.06)" : border}`,
                    borderRadius: "14px",
                    padding: "14px 16px",
                    display: "flex",
                    flexDirection: "column",
                    gap: "8px"
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      {isCrit ? (
                        <AlertOctagon size={16} color="#ef4444" />
                      ) : (
                        <AlertTriangle size={16} color="#f59e0b" />
                      )}
                      <h4 style={{ fontSize: "14px", fontWeight: "700", color: "#ffffff" }}>
                        {alert.title}
                      </h4>
                    </div>

                    <span style={{ fontSize: "10px", color: "var(--text-dim)" }}>
                      {new Date(alert.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>

                  <p style={{ fontSize: "12px", color: "#cbd5e1", lineHeight: "1.4" }}>
                    {alert.message}
                  </p>

                  {alert.recommendation && (
                    <div style={{
                      background: "rgba(0, 0, 0, 0.25)",
                      padding: "8px 10px",
                      borderRadius: "8px",
                      fontSize: "11px",
                      color: "#93c5fd"
                    }}>
                      💡 Recommendation: {alert.recommendation}
                    </div>
                  )}

                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "4px" }}>
                    <span style={{ fontSize: "10px", color: "var(--text-muted)" }}>
                      Node: {alert.device_id} • Channel: {alert.channel}
                    </span>

                    <div style={{ display: "flex", gap: "6px" }}>
                      {onConvertToAction && !alert.acknowledged && (
                        <button
                          onClick={() => onConvertToAction(alert.id)}
                          className="btn-primary"
                          style={{ fontSize: "11px", padding: "4px 10px" }}
                        >
                          <Sparkles size={12} />
                          <span>Take Action</span>
                        </button>
                      )}

                      {!alert.acknowledged && (
                        <button
                          onClick={() => onAcknowledge(alert.id)}
                          className="btn-secondary"
                          style={{ fontSize: "11px", padding: "4px 10px" }}
                        >
                          <Check size={12} />
                          <span>Acknowledge</span>
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

      </div>
    </div>
  );
};
