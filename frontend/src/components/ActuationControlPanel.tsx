import React, { useState, useEffect } from "react";
import { Sliders, Zap, Wind, ShieldCheck, Activity, RefreshCw, Power, CheckCircle, AlertTriangle } from "lucide-react";
import type { ActuatorDevice, ActuationLog } from "../types";
import { fetchActuators, controlActuator, fetchActuationLogs, evaluateActuation } from "../api";

interface ActuationControlPanelProps {
  selectedDeviceId: string;
  onActionTriggered?: (msg: string) => void;
}

export const ActuationControlPanel: React.FC<ActuationControlPanelProps> = ({
  selectedDeviceId,
  onActionTriggered,
}) => {
  const [actuators, setActuators] = useState<ActuatorDevice[]>([]);
  const [logs, setLogs] = useState<ActuationLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [devList, logList] = await Promise.all([
        fetchActuators(),
        fetchActuationLogs(undefined, 8),
      ]);
      setActuators(devList);
      setLogs(logList);
    } catch (e: any) {
      console.error("Error loading actuation data:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleCommand = async (actuatorId: string, command: string, speedPct = 100) => {
    try {
      const updated = await controlActuator(actuatorId, command, speedPct, "DASHBOARD_UI", "Manual user adjustment");
      setActuators((prev) => prev.map((a) => (a.actuator_id === actuatorId ? updated : a)));
      setStatusMsg(`Command ${command} sent to ${actuatorId}`);
      onActionTriggered?.(`Actuated ${actuatorId} -> ${command} (${speedPct}%)`);
      setTimeout(() => setStatusMsg(null), 3000);
      loadData();
    } catch (err: any) {
      setStatusMsg(`Error: ${err.message}`);
    }
  };

  const handleEvaluateML = async () => {
    setEvaluating(true);
    try {
      const res = await evaluateActuation(selectedDeviceId);
      setStatusMsg(res.message);
      onActionTriggered?.(res.message);
      setTimeout(() => setStatusMsg(null), 4000);
      loadData();
    } catch (err: any) {
      setStatusMsg(`Evaluation error: ${err.message}`);
    } finally {
      setEvaluating(false);
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
            background: "linear-gradient(135deg, rgba(56, 189, 248, 0.2), rgba(168, 85, 247, 0.2))",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            border: "1px solid rgba(56, 189, 248, 0.3)"
          }}>
            <Sliders size={20} color="#38bdf8" />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <h3 style={{ fontSize: "16px", fontWeight: "700", color: "#f8fafc", margin: 0 }}>
                Closed-Loop Smart Actuation Hub
              </h3>
              <span style={{
                fontSize: "10px",
                padding: "2px 8px",
                borderRadius: "12px",
                background: "rgba(16, 185, 129, 0.15)",
                color: "#10b981",
                border: "1px solid rgba(16, 185, 129, 0.3)",
                fontWeight: "600"
              }}>
                Matter / HA / Relays
              </span>
            </div>
            <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: "2px 0 0 0" }}>
              Autonomous remediation, fan modulation & CADR filter decay tracking
            </p>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <button
            onClick={handleEvaluateML}
            disabled={evaluating}
            style={{
              padding: "6px 12px",
              borderRadius: "8px",
              background: "linear-gradient(135deg, #0284c7, #2563eb)",
              color: "#ffffff",
              fontSize: "12px",
              fontWeight: "600",
              border: "none",
              cursor: evaluating ? "not-allowed" : "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px",
              boxShadow: "0 2px 8px rgba(37, 99, 235, 0.3)"
            }}
          >
            <Zap size={14} />
            {evaluating ? "Evaluating..." : "Evaluate ML Rules"}
          </button>

          <button
            onClick={loadData}
            style={{
              padding: "6px 10px",
              borderRadius: "8px",
              background: "rgba(255, 255, 255, 0.05)",
              color: "var(--text-muted)",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "4px",
              fontSize: "12px"
            }}
          >
            <RefreshCw size={13} className={loading ? "spin-animate" : ""} />
            Sync
          </button>
        </div>
      </div>

      {statusMsg && (
        <div style={{
          padding: "8px 12px",
          borderRadius: "8px",
          background: "rgba(56, 189, 248, 0.1)",
          border: "1px solid rgba(56, 189, 248, 0.3)",
          color: "#38bdf8",
          fontSize: "12px",
          marginBottom: "14px",
          display: "flex",
          alignItems: "center",
          gap: "8px"
        }}>
          <CheckCircle size={14} />
          {statusMsg}
        </div>
      )}

      {/* Actuator Cards Grid */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
        gap: "12px",
        marginBottom: "18px"
      }}>
        {actuators.map((act) => {
          const isActive = act.state !== "OFF";
          const isFilterDegraded = act.filter_health_pct < 60;
          return (
            <div
              key={act.actuator_id}
              style={{
                padding: "14px",
                borderRadius: "12px",
                background: isActive ? "rgba(15, 23, 42, 0.8)" : "rgba(15, 23, 42, 0.4)",
                border: `1px solid ${isActive ? "rgba(56, 189, 248, 0.3)" : "rgba(255, 255, 255, 0.06)"}`,
                display: "flex",
                flexDirection: "column",
                gap: "10px",
                position: "relative",
              }}
            >
              {/* Card Header */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <span style={{ fontSize: "14px", fontWeight: "700", color: "#f8fafc" }}>
                      {act.name}
                    </span>
                    <span style={{
                      fontSize: "9px",
                      padding: "2px 6px",
                      borderRadius: "6px",
                      background: "rgba(255, 255, 255, 0.08)",
                      color: "var(--text-muted)",
                      fontWeight: "600"
                    }}>
                      {act.protocol}
                    </span>
                  </div>
                  <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                    Bound to: {act.room_binding} ({act.device_type})
                  </span>
                </div>

                <span style={{
                  fontSize: "11px",
                  padding: "2px 8px",
                  borderRadius: "10px",
                  background: isActive ? "rgba(16, 185, 129, 0.15)" : "rgba(148, 163, 184, 0.15)",
                  color: isActive ? "#10b981" : "#94a3b8",
                  fontWeight: "700"
                }}>
                  {act.state} ({act.speed_pct}%)
                </span>
              </div>

              {/* Filter Health & CADR metric */}
              <div style={{
                background: "rgba(0, 0, 0, 0.25)",
                padding: "8px 10px",
                borderRadius: "8px",
                border: "1px solid rgba(255, 255, 255, 0.04)"
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", marginBottom: "4px" }}>
                  <span style={{ color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "4px" }}>
                    <Wind size={12} color="#38bdf8" /> CADR: {act.filter_cadr_cfm} CFM
                  </span>
                  <span style={{
                    color: isFilterDegraded ? "#f59e0b" : "#10b981",
                    fontWeight: "600"
                  }}>
                    Filter: {act.filter_health_pct.toFixed(0)}%
                  </span>
                </div>
                <div style={{
                  height: "4px",
                  width: "100%",
                  background: "rgba(255, 255, 255, 0.08)",
                  borderRadius: "2px",
                  overflow: "hidden"
                }}>
                  <div style={{
                    height: "100%",
                    width: `${act.filter_health_pct}%`,
                    background: isFilterDegraded ? "#f59e0b" : "#10b981",
                  }} />
                </div>
              </div>

              {/* Control Action Buttons */}
              <div style={{ display: "flex", gap: "6px", alignItems: "center", marginTop: "2px" }}>
                <button
                  onClick={() => handleCommand(act.actuator_id, act.state === "OFF" ? "AUTO" : "OFF", 0)}
                  style={{
                    flex: "1",
                    padding: "6px",
                    borderRadius: "6px",
                    background: isActive ? "rgba(239, 68, 68, 0.15)" : "rgba(16, 185, 129, 0.15)",
                    color: isActive ? "#ef4444" : "#10b981",
                    border: `1px solid ${isActive ? "rgba(239, 68, 68, 0.3)" : "rgba(16, 185, 129, 0.3)"}`,
                    fontSize: "11px",
                    fontWeight: "600",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "4px"
                  }}
                >
                  <Power size={12} />
                  {isActive ? "Turn OFF" : "Turn ON"}
                </button>

                <button
                  onClick={() => handleCommand(act.actuator_id, "SET_SPEED", 50)}
                  style={{
                    padding: "6px 10px",
                    borderRadius: "6px",
                    background: "rgba(255, 255, 255, 0.05)",
                    color: "#f8fafc",
                    border: "1px solid rgba(255, 255, 255, 0.1)",
                    fontSize: "11px",
                    cursor: "pointer"
                  }}
                >
                  50%
                </button>

                <button
                  onClick={() => handleCommand(act.actuator_id, "SET_SPEED", 100)}
                  style={{
                    padding: "6px 10px",
                    borderRadius: "6px",
                    background: "rgba(56, 189, 248, 0.15)",
                    color: "#38bdf8",
                    border: "1px solid rgba(56, 189, 248, 0.3)",
                    fontSize: "11px",
                    fontWeight: "600",
                    cursor: "pointer"
                  }}
                >
                  Max 100%
                </button>

                <button
                  onClick={() => handleCommand(act.actuator_id, "SET_MODE", 75)}
                  style={{
                    padding: "6px 10px",
                    borderRadius: "6px",
                    background: "rgba(168, 85, 247, 0.15)",
                    color: "#c084fc",
                    border: "1px solid rgba(168, 85, 247, 0.3)",
                    fontSize: "11px",
                    cursor: "pointer"
                  }}
                >
                  Auto ML
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Actuation Log Trail */}
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
          <span style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "6px" }}>
            <Activity size={13} color="#38bdf8" /> Real-Time Closed-Loop Audit Trail
          </span>
          <span style={{ fontSize: "11px", color: "var(--text-dim)" }}>
            Cumulative Energy Logged
          </span>
        </div>

        <div style={{
          display: "flex",
          flexDirection: "column",
          gap: "6px",
          maxHeight: "160px",
          overflowY: "auto"
        }}>
          {logs.length === 0 ? (
            <div style={{ fontSize: "12px", color: "var(--text-dim)", fontStyle: "italic", textAlign: "center", padding: "10px" }}>
              No recent automated actuation dispatches recorded yet.
            </div>
          ) : (
            logs.map((lg) => (
              <div
                key={lg.id}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "6px 10px",
                  borderRadius: "8px",
                  background: "rgba(255, 255, 255, 0.02)",
                  border: "1px solid rgba(255, 255, 255, 0.04)",
                  fontSize: "11px"
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ fontWeight: "700", color: "#38bdf8" }}>{lg.actuator_id}</span>
                  <span style={{ color: "#f8fafc" }}>{lg.command} ({lg.speed_pct}%)</span>
                  <span style={{ color: "var(--text-muted)" }}>• {lg.reason}</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <span style={{ color: "#10b981", fontWeight: "600" }}>
                    {lg.energy_wh_consumed > 0 ? `${lg.energy_wh_consumed.toFixed(1)} Wh` : "0.5 Wh"}
                  </span>
                  <span style={{ color: "var(--text-dim)" }}>
                    {new Date(lg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
