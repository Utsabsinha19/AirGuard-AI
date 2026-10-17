import React, { useState, useEffect } from "react";
import {
  Building2,
  Sliders,
  Power,
  RefreshCw,
  Cpu,
  Layers,
  Zap,
  Activity,
  CheckCircle2
} from "lucide-react";
import type { BMSDevice } from "../types";
import { fetchBMSDevices, controlBMSDevice } from "../api";

export const BMSIndustrialPanel: React.FC = () => {
  const [devices, setDevices] = useState<BMSDevice[]>([]);
  const [loading, setLoading] = useState(false);
  const [controllingId, setControllingId] = useState<string | null>(null);

  const loadDevices = () => {
    setLoading(true);
    fetchBMSDevices()
      .then(setDevices)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDevices();
  }, []);

  const handleUpdate = async (devId: string, speed: number, damper: number) => {
    setControllingId(devId);
    try {
      const updated = await controlBMSDevice(devId, speed, damper);
      setDevices((prev) => prev.map((d) => (d.id === devId ? updated : d)));
    } catch (e) {
      console.error(e);
    } finally {
      setControllingId(null);
    }
  };

  const getProtocolBadge = (proto: string) => {
    if (proto === "BACNET_IP") return { color: "#38bdf8", label: "BACnet/IP (ASHRAE 135)" };
    if (proto === "MODBUS_TCP") return { color: "#facc15", label: "Modbus TCP (PLC)" };
    if (proto === "KNX") return { color: "#4ade80", label: "KNX Automation" };
    return { color: "#c084fc", label: "Sparkplug B (MQTT)" };
  };

  return (
    <div className="card" style={{ padding: "1.25rem", borderRadius: "1rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
          <div style={{ background: "rgba(14, 165, 233, 0.15)", padding: "0.5rem", borderRadius: "0.6rem", color: "#38bdf8" }}>
            <Building2 size={20} />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700 }}>Industrial BMS & Smart Facilities Actuation</h3>
              <span className="badge" style={{ background: "rgba(14, 165, 233, 0.2)", color: "#7dd3fc" }}>
                Commercial Grid
              </span>
            </div>
            <p style={{ margin: 0, fontSize: "0.78rem", color: "var(--text-muted)" }}>
              Direct register modulation for commercial HVAC chillers, VAV dampers, AHU inverters & scrubbers
            </p>
          </div>
        </div>

        <button
          className="btn btn-secondary"
          onClick={loadDevices}
          disabled={loading}
          style={{ fontSize: "0.8rem", padding: "0.4rem 0.85rem", display: "flex", alignItems: "center", gap: "0.4rem" }}
        >
          <RefreshCw size={14} className={loading ? "spin" : ""} />
          Refresh Registers
        </button>
      </div>

      {/* Equipment List */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "0.75rem" }}>
        {devices.map((dev) => {
          const pb = getProtocolBadge(dev.protocol);
          const isBusy = controllingId === dev.id;
          return (
            <div
              key={dev.id}
              style={{
                background: "rgba(255, 255, 255, 0.03)",
                border: "1px solid var(--border)",
                borderRadius: "0.75rem",
                padding: "0.85rem",
                display: "flex",
                flexDirection: "column",
                gap: "0.5rem"
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontWeight: 700, fontSize: "0.9rem", color: "#f8fafc" }}>{dev.name}</span>
                <span className="badge" style={{ fontSize: "0.68rem", color: pb.color, background: "rgba(255,255,255,0.06)" }}>
                  {dev.protocol}
                </span>
              </div>

              <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                Point Register: <code>{dev.point_name}</code>
              </div>

              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem" }}>
                <span>Power Draw: <strong style={{ color: "#facc15" }}>{dev.power_draw_kw} kW</strong></span>
                <span>State: <strong style={{ color: dev.current_state.includes("RUNNING") || dev.current_state.includes("MODULATING") ? "#4ade80" : "#94a3b8" }}>{dev.current_state}</strong></span>
              </div>

              {/* Sliders */}
              <div style={{ marginTop: "0.2rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.72rem", color: "var(--text-muted)" }}>
                  <span>Speed / Output: {dev.speed_pct}%</span>
                  <span>Damper Position: {dev.damper_pct}%</span>
                </div>
                <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.25rem" }}>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    step="5"
                    value={dev.speed_pct}
                    onChange={(e) => handleUpdate(dev.id, parseInt(e.target.value), dev.damper_pct)}
                    disabled={isBusy}
                    style={{ flex: 1 }}
                  />
                  <input
                    type="range"
                    min="0"
                    max="100"
                    step="5"
                    value={dev.damper_pct}
                    onChange={(e) => handleUpdate(dev.id, dev.speed_pct, parseInt(e.target.value))}
                    disabled={isBusy}
                    style={{ flex: 1 }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
