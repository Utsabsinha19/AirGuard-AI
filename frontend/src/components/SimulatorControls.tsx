import React, { useState } from "react";
import { Cpu, X, Flame, Wind, Sparkles, WifiOff, RefreshCw, CheckCircle2 } from "lucide-react";
import { triggerSimulatorScenario } from "../api";

interface SimulatorControlsProps {
  isOpen: boolean;
  onClose: () => void;
  selectedDeviceId: string;
  onScenarioTriggered: (msg: string) => void;
}

export const SimulatorControls: React.FC<SimulatorControlsProps> = ({
  isOpen,
  onClose,
  selectedDeviceId,
  onScenarioTriggered,
}) => {
  const [loadingScenario, setLoadingScenario] = useState<string | null>(null);

  if (!isOpen) return null;

  const scenarios = [
    {
      id: "COOKING_SMOKE",
      name: "Cooking & Frying Smoke",
      targetRoom: "Kitchen (AG-003)",
      desc: "Simultaneous PM2.5 (68 µg/m³) and VOC (485 ppb) surge. Triggers culinary diagnosis.",
      icon: <Flame size={18} color="#f97316" />,
      device: "AG-003",
    },
    {
      id: "POOR_VENTILATION",
      name: "Poor Ventilation / CO₂ Buildup",
      targetRoom: "Bedroom (AG-001)",
      desc: "CO2 rises to 1580 ppm alongside metabolic VOCs. Triggers stagnant air warning.",
      icon: <Wind size={18} color="#a855f7" />,
      device: "AG-001",
    },
    {
      id: "CHEMICAL_CLEANER",
      name: "Chemical Cleaner / Solvents",
      targetRoom: "Office (AG-004)",
      desc: "Isolated sharp spike in VOC (720 ppb) while particulate levels remain baseline.",
      icon: <Sparkles size={18} color="#ec4899" />,
      device: "AG-004",
    },
    {
      id: "OPEN_WINDOW",
      name: "Open Window (Fresh Air Dilution)",
      targetRoom: "Current Selected Room",
      desc: "Rapid dilution curve toward clean ambient baseline (PM 5.4, CO2 430 ppm).",
      icon: <Wind size={18} color="#10b981" />,
      device: selectedDeviceId,
    },
    {
      id: "OFFLINE_BUFFER_BURST",
      name: "Wi-Fi Outage & Buffer Drain (FR-2.3)",
      targetRoom: "Current Selected Room",
      desc: "Simulates network reconnection: bursts 8 buffered records stored during outage.",
      icon: <WifiOff size={18} color="#38bdf8" />,
      device: selectedDeviceId,
    },
    {
      id: "RESET_NOMINAL",
      name: "Reset to Clean Nominal Baseline",
      targetRoom: "Current Selected Room",
      desc: "Restores clean indoor conditions across all sensors.",
      icon: <RefreshCw size={18} color="#94a3b8" />,
      device: selectedDeviceId,
    },
  ];

  const handleTrigger = async (scenarioId: string, deviceId: string) => {
    setLoadingScenario(scenarioId);
    try {
      const res = await triggerSimulatorScenario(scenarioId, deviceId);
      onScenarioTriggered(res.message);
    } catch (err: any) {
      onScenarioTriggered(`Failed to trigger: ${err.message}`);
    } finally {
      setLoadingScenario(null);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="glass-panel"
        style={{
          width: "100%",
          maxWidth: "540px",
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
            <Cpu size={22} color="#a855f7" />
            <div>
              <h3 style={{ fontSize: "18px", fontWeight: "700", color: "#ffffff" }}>
                Virtual IoT Edge Node Simulator
              </h3>
              <p style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                Test anomaly detection, root cause diagnostics, and offline queue flushing
              </p>
            </div>
          </div>

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

        {/* Scenarios Grid */}
        <div style={{ display: "flex", flexDirection: "column", gap: "10px", maxHeight: "65vh", overflowY: "auto" }}>
          {scenarios.map((sc) => (
            <div
              key={sc.id}
              style={{
                background: "rgba(255, 255, 255, 0.03)",
                border: "1px solid rgba(255, 255, 255, 0.08)",
                borderRadius: "14px",
                padding: "14px 16px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                gap: "12px"
              }}
            >
              <div style={{ display: "flex", alignItems: "flex-start", gap: "12px", flex: 1 }}>
                <div style={{
                  background: "rgba(255, 255, 255, 0.05)",
                  padding: "8px",
                  borderRadius: "10px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center"
                }}>
                  {sc.icon}
                </div>
                <div>
                  <h4 style={{ fontSize: "14px", fontWeight: "700", color: "#ffffff" }}>
                    {sc.name}
                  </h4>
                  <span style={{ fontSize: "11px", color: "#38bdf8", fontWeight: "600", display: "block", marginTop: "1px" }}>
                    Target: {sc.targetRoom}
                  </span>
                  <p style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "3px", lineHeight: "1.3" }}>
                    {sc.desc}
                  </p>
                </div>
              </div>

              <button
                onClick={() => handleTrigger(sc.id, sc.device)}
                disabled={loadingScenario === sc.id}
                className="btn-primary"
                style={{ fontSize: "11px", padding: "7px 12px", whiteSpace: "nowrap" }}
              >
                {loadingScenario === sc.id ? "Injecting..." : "Inject"}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
