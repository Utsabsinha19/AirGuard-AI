import React, { useState } from "react";
import { Cpu, X, Flame, Wind, Sparkles, WifiOff, RefreshCw, CheckCircle2, ShieldAlert, Users, CloudRain } from "lucide-react";
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
      id: "MATERIAL_OFF_GASSING",
      name: "Material Off-Gassing (v3.0)",
      targetRoom: "Bedroom (AG-001)",
      desc: "Severe HCHO surge to 0.145 ppm & VOC Index 420. Triggers off-gassing remediation.",
      icon: <Sparkles size={18} color="#f43f5e" />,
      device: "AG-001",
    },
    {
      id: "WILDFIRE_SMOKE",
      name: "Wildfire Smoke Infiltration (v3.0)",
      targetRoom: "Living Room (AG-002)",
      desc: "Ultrafine PM0.3 (48 µg/m³) & PM2.5 (115 µg/m³) smoke plume. Triggers sealed HVAC recirculation.",
      icon: <Flame size={18} color="#ea580c" />,
      device: "AG-002",
    },
    {
      id: "COOKING_SMOKE",
      name: "Cooking & Frying Smoke (v2.0)",
      targetRoom: "Kitchen (AG-003)",
      desc: "Simultaneous PM2.5 (68 µg/m³) and VOC (485 ppb) surge. Triggers culinary diagnosis.",
      icon: <Flame size={18} color="#f97316" />,
      device: "AG-003",
    },
    {
      id: "POOR_VENTILATION",
      name: "Occupancy Stagnation (v2.0)",
      targetRoom: "Bedroom (AG-001)",
      desc: "CO2 rises to 1580 ppm alongside metabolic VOCs. Triggers stagnant air warning.",
      icon: <Wind size={18} color="#a855f7" />,
      device: "AG-001",
    },
    {
      id: "HVAC_FILTER_FAILURE",
      name: "HVAC / Filter Failure (v2.0)",
      targetRoom: "Living Room (AG-002)",
      desc: "Gradual rise in PM2.5 (24.5), PM10 (36), and humidity (58.5%). Triggers filter alert.",
      icon: <ShieldAlert size={18} color="#eab308" />,
      device: "AG-002",
    },
    {
      id: "CHEMICAL_CLEANER",
      name: "Volatile Chemical Event (v2.0)",
      targetRoom: "Office (AG-004)",
      desc: "Isolated sharp spike in VOC (720 ppb) while particulate levels remain baseline.",
      icon: <Sparkles size={18} color="#ec4899" />,
      device: "AG-004",
    },
    {
      id: "HIGH_OCCUPANCY",
      name: "High Occupancy Gathering (v2.0)",
      targetRoom: "Living Room (AG-002)",
      desc: "Concurrent CO2 (1450 ppm), metabolic VOC (340 ppb), and acoustic noise (74 dB).",
      icon: <Users size={18} color="#06b6d4" />,
      device: "AG-002",
    },
    {
      id: "WEATHER_INVERSION",
      name: "Weather Inversion & Smog (v2.0)",
      targetRoom: "Outdoor (AG-005)",
      desc: "Barometric drop to 1003.5 hPa accompanied by fine particulate smog (38 µg/m³).",
      icon: <CloudRain size={18} color="#6366f1" />,
      device: "AG-005",
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
      name: "Wi-Fi Outage & Buffer Drain (v2.0)",
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
