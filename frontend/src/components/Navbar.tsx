import React from "react";
import { Device, AlertItem } from "../types";
import { ShieldAlert, Bell, Cpu, Radio, Sparkles } from "lucide-react";

interface NavbarProps {
  devices: Device[];
  selectedDeviceId: string;
  onSelectDevice: (id: string) => void;
  isConnected: boolean;
  modelType: "baseline" | "neural";
  onToggleModel: (type: "baseline" | "neural") => void;
  alerts: AlertItem[];
  onOpenAlerts: () => void;
  onOpenSimulator: () => void;
  onOpenActionModal: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  devices,
  selectedDeviceId,
  onSelectDevice,
  isConnected,
  modelType,
  onToggleModel,
  alerts,
  onOpenAlerts,
  onOpenSimulator,
  onOpenActionModal,
}) => {
  const unackCount = alerts.filter((a) => !a.acknowledged).length;
  const currentDevice = devices.find((d) => d.id === selectedDeviceId);

  return (
    <header className="glass-panel" style={{ margin: "16px 24px", padding: "14px 24px", borderRadius: "18px" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "16px" }}>
        
        {/* Brand & Live Stream Status */}
        <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
          <div style={{
            background: "linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)",
            borderRadius: "12px",
            width: "40px",
            height: "40px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 0 16px rgba(99, 102, 241, 0.4)"
          }}>
            <Radio size={22} color="#ffffff" />
          </div>

          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <h1 style={{ fontSize: "20px", fontWeight: "800", letterSpacing: "-0.02em", color: "#f8fafc" }}>
                AirGuard AI
              </h1>
              <span className="glass-pill" style={{ fontSize: "11px", fontWeight: "600", color: "#38bdf8", border: "1px solid rgba(56, 189, 248, 0.3)" }}>
                v1.2 IoT Edge
              </span>
            </div>
            <p style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>
              Personal Air Quality Intelligence & Multi-Horizon Predictor
            </p>
          </div>

          {/* Real-time WebSocket connection badge (NFR-1) */}
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            padding: "5px 12px",
            borderRadius: "9999px",
            background: isConnected ? "rgba(16, 185, 129, 0.12)" : "rgba(239, 68, 68, 0.12)",
            border: `1px solid ${isConnected ? "rgba(16, 185, 129, 0.3)" : "rgba(239, 68, 68, 0.3)"}`,
            marginLeft: "8px"
          }}>
            <div className={isConnected ? "pulse-dot" : ""} style={{
              width: "8px",
              height: "8px",
              borderRadius: "50%",
              background: isConnected ? "#10b981" : "#ef4444"
            }} />
            <span style={{ fontSize: "11px", fontWeight: "600", color: isConnected ? "#10b981" : "#ef4444" }}>
              {isConnected ? "LIVE STREAM (< 1s)" : "CONNECTING..."}
            </span>
          </div>
        </div>

        {/* Right Controls: Room Selector, Model Switcher, Alert Bell, Action Tracker, Simulator */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
          
          {/* Room Selector */}
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: "500" }}>Room:</span>
            <select
              value={selectedDeviceId}
              onChange={(e) => onSelectDevice(e.target.value)}
              style={{
                background: "rgba(15, 23, 42, 0.8)",
                border: "1px solid rgba(255, 255, 255, 0.14)",
                color: "#f8fafc",
                borderRadius: "10px",
                padding: "7px 12px",
                fontSize: "13px",
                fontWeight: "600",
                outline: "none",
                cursor: "pointer"
              }}
            >
              {devices.map((d) => (
                <option key={d.id} value={d.id} style={{ background: "#0f172a" }}>
                  {d.room} ({d.id})
                </option>
              ))}
            </select>
          </div>

          {/* Model Mode Toggle (Phase A vs Phase B) */}
          <div style={{
            display: "flex",
            alignItems: "center",
            background: "rgba(255, 255, 255, 0.05)",
            borderRadius: "10px",
            padding: "3px",
            border: "1px solid rgba(255, 255, 255, 0.1)"
          }}>
            <button
              onClick={() => onToggleModel("baseline")}
              style={{
                background: modelType === "baseline" ? "rgba(99, 102, 241, 0.8)" : "transparent",
                color: modelType === "baseline" ? "#ffffff" : "var(--text-muted)",
                border: "none",
                borderRadius: "7px",
                padding: "5px 10px",
                fontSize: "11px",
                fontWeight: "600",
                cursor: "pointer",
                transition: "all 0.15s ease"
              }}
            >
              Phase A: GBM
            </button>
            <button
              onClick={() => onToggleModel("neural")}
              style={{
                background: modelType === "neural" ? "rgba(6, 182, 212, 0.8)" : "transparent",
                color: modelType === "neural" ? "#ffffff" : "var(--text-muted)",
                border: "none",
                borderRadius: "7px",
                padding: "5px 10px",
                fontSize: "11px",
                fontWeight: "600",
                cursor: "pointer",
                transition: "all 0.15s ease"
              }}
            >
              Phase B: PyTorch
            </button>
          </div>

          {/* Log Intervention Action Button */}
          <button
            onClick={onOpenActionModal}
            className="btn-secondary"
            style={{ fontSize: "12px", padding: "7px 12px" }}
            title="Log remediation action (Open window, HEPA purifier)"
          >
            <Sparkles size={15} color="#38bdf8" />
            <span>Log Action</span>
          </button>

          {/* Simulator Drawer Button */}
          <button
            onClick={onOpenSimulator}
            className="btn-secondary"
            style={{ fontSize: "12px", padding: "7px 12px" }}
            title="Trigger virtual IoT edge anomaly scenarios"
          >
            <Cpu size={15} color="#a855f7" />
            <span>IoT Simulator</span>
          </button>

          {/* Alert Center Bell */}
          <button
            onClick={onOpenAlerts}
            className="btn-secondary"
            style={{ position: "relative", padding: "7px 11px" }}
            title="Alert Notifications"
          >
            <Bell size={17} color={unackCount > 0 ? "#ef4444" : "#94a3b8"} />
            {unackCount > 0 && (
              <span style={{
                position: "absolute",
                top: "-4px",
                right: "-4px",
                background: "#ef4444",
                color: "#ffffff",
                fontSize: "10px",
                fontWeight: "700",
                width: "18px",
                height: "18px",
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 0 8px rgba(239, 68, 68, 0.6)"
              }}>
                {unackCount}
              </span>
            )}
          </button>

        </div>
      </div>
    </header>
  );
};
