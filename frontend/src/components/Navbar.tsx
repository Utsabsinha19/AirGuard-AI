import React from "react";
import type { Device, AlertItem } from "../types";
import { Bell, Cpu, Radio, Sparkles, Sliders, Download, Map } from "lucide-react";
import { getExportCSVUrl } from "../api";

interface NavbarProps {
  devices: Device[];
  selectedDeviceId: string;
  onSelectDevice: (id: string) => void;
  isConnected: boolean;
  modelType: string;
  onSelectModel: (type: string) => void;
  alerts: AlertItem[];
  onOpenAlerts: () => void;
  onOpenSimulator: () => void;
  onOpenActionModal: () => void;
  onOpenModelComparison: () => void;
  onOpenCalibration: () => void;
  showFloorplan: boolean;
  onToggleFloorplan: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  devices,
  selectedDeviceId,
  onSelectDevice,
  isConnected,
  modelType,
  onSelectModel,
  alerts,
  onOpenAlerts,
  onOpenSimulator,
  onOpenActionModal,
  onOpenModelComparison,
  onOpenCalibration,
  showFloorplan,
  onToggleFloorplan,
}) => {
  const unackCount = alerts.filter((a) => !a.acknowledged).length;

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
                v1.3.0 Pro
              </span>
            </div>
            <p style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>
              Personal Environmental Intelligence & Deep Sequence Predictor
            </p>
          </div>

          {/* Sub-second WebSocket stream badge */}
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

        {/* Right Controls */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
          
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

          {/* Model Architecture Switcher (Section 2.2 Suggestion 1) */}
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: "500" }}>AI Model:</span>
            <select
              value={modelType}
              onChange={(e) => onSelectModel(e.target.value)}
              style={{
                background: "rgba(15, 23, 42, 0.8)",
                border: "1px solid rgba(255, 255, 255, 0.14)",
                color: "#38bdf8",
                borderRadius: "10px",
                padding: "7px 12px",
                fontSize: "12px",
                fontWeight: "600",
                outline: "none",
                cursor: "pointer"
              }}
            >
              <option value="baseline" style={{ background: "#0f172a" }}>Phase A: GBM Trees</option>
              <option value="lstm" style={{ background: "#0f172a" }}>Phase B: PyTorch LSTM</option>
              <option value="gru" style={{ background: "#0f172a" }}>Phase B: PyTorch GRU</option>
              <option value="tcn" style={{ background: "#0f172a" }}>Phase B: Temporal CNN</option>
            </select>
          </div>

          {/* Floorplan View Toggle */}
          <button
            onClick={onToggleFloorplan}
            className="btn-secondary"
            style={{
              fontSize: "12px",
              padding: "7px 12px",
              background: showFloorplan ? "rgba(56, 189, 248, 0.2)" : undefined,
              borderColor: showFloorplan ? "#38bdf8" : undefined
            }}
            title="Toggle 2D Floorplan blueprint view"
          >
            <Map size={15} color="#38bdf8" />
            <span>Floorplan</span>
          </button>

          {/* Multi-Model Benchmark Comparison Button */}
          <button
            onClick={onOpenModelComparison}
            className="btn-secondary"
            style={{ fontSize: "12px", padding: "7px 12px" }}
            title="Compare GBM, LSTM, GRU, and Temporal CNN benchmarks"
          >
            <Cpu size={15} color="#a855f7" />
            <span>Model Benchmarks</span>
          </button>

          {/* Sensor Calibration Button */}
          <button
            onClick={onOpenCalibration}
            className="btn-secondary"
            style={{ fontSize: "12px", padding: "7px 12px" }}
            title="Calibrate sensor zero offset and gain"
          >
            <Sliders size={15} color="#06b6d4" />
            <span>Calibrate</span>
          </button>

          {/* CSV Export Link */}
          <a
            href={getExportCSVUrl(selectedDeviceId)}
            download
            className="btn-secondary"
            style={{ fontSize: "12px", padding: "7px 12px", textDecoration: "none" }}
            title="Download historical telemetry CSV report"
          >
            <Download size={15} color="#10b981" />
            <span>Export CSV</span>
          </a>

          {/* Log Action Button */}
          <button
            onClick={onOpenActionModal}
            className="btn-secondary"
            style={{ fontSize: "12px", padding: "7px 12px" }}
          >
            <Sparkles size={15} color="#38bdf8" />
            <span>Log Action</span>
          </button>

          {/* Simulator Drawer Button */}
          <button
            onClick={onOpenSimulator}
            className="btn-secondary"
            style={{ fontSize: "12px", padding: "7px 12px" }}
          >
            <Cpu size={15} color="#ec4899" />
            <span>Simulator</span>
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
