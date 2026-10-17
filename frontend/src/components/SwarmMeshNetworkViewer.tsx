import React, { useState, useEffect } from "react";
import {
  Share2,
  Wifi,
  Radio,
  Cpu,
  Layers,
  Battery,
  ShieldCheck,
  RefreshCw,
  GitFork,
  ArrowRight
} from "lucide-react";
import type { MeshTopologyResponse, PeerConsensusReport } from "../types";
import { fetchMeshTopology, triggerPeerConsensus } from "../api";

export const SwarmMeshNetworkViewer: React.FC = () => {
  const [topology, setTopology] = useState<MeshTopologyResponse | null>(null);
  const [consensusReport, setConsensusReport] = useState<PeerConsensusReport | null>(null);
  const [calibrating, setCalibrating] = useState(false);

  useEffect(() => {
    fetchMeshTopology().then(setTopology).catch(console.error);
  }, []);

  const handleRunConsensus = async () => {
    setCalibrating(true);
    try {
      const res = await triggerPeerConsensus();
      setConsensusReport(res);
    } catch (e) {
      console.error(e);
    } finally {
      setCalibrating(false);
    }
  };

  const getTransportBadge = (transport: string) => {
    if (transport === "WIFI") return { color: "#38bdf8", bg: "rgba(56, 189, 248, 0.15)", label: "Wi-Fi Uplink" };
    if (transport === "ESP_NOW_MESH") return { color: "#a855f7", bg: "rgba(168, 85, 247, 0.15)", label: "ESP-NOW Peer Mesh" };
    if (transport === "CELLULAR_NBIOT") return { color: "#facc15", bg: "rgba(250, 204, 21, 0.15)", label: "Cellular NB-IoT" };
    return { color: "#f43f5e", bg: "rgba(244, 63, 94, 0.15)", label: "LoRaWAN Fallback" };
  };

  return (
    <div className="card" style={{ padding: "1.25rem", borderRadius: "1rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
          <div style={{ background: "rgba(168, 85, 247, 0.15)", padding: "0.5rem", borderRadius: "0.6rem", color: "#c084fc" }}>
            <Share2 size={20} />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700 }}>Zero-Infrastructure ESP-NOW Swarm Mesh</h3>
              <span className="badge" style={{ background: "rgba(16, 185, 129, 0.2)", color: "#6ee7b7" }}>
                Multi-Hop Peer Mesh
              </span>
            </div>
            <p style={{ margin: 0, fontSize: "0.78rem", color: "var(--text-muted)" }}>
              Self-healing multi-transport grid (Wi-Fi → ESP-NOW → Cellular/LoRaWAN) & on-device consensus drift calibration
            </p>
          </div>
        </div>

        <button
          className="btn btn-secondary"
          onClick={handleRunConsensus}
          disabled={calibrating}
          style={{ fontSize: "0.8rem", padding: "0.4rem 0.85rem", display: "flex", alignItems: "center", gap: "0.4rem" }}
        >
          <RefreshCw size={14} className={calibrating ? "spin" : ""} />
          {calibrating ? "Consensus Calibrating..." : "Trigger Peer Consensus"}
        </button>
      </div>

      {/* Consensus Calibration Feedback Banner */}
      {consensusReport && (
        <div
          style={{
            marginBottom: "1rem",
            padding: "0.75rem 1rem",
            borderRadius: "0.75rem",
            background: "rgba(16, 185, 129, 0.12)",
            border: "1px solid rgba(16, 185, 129, 0.3)",
            fontSize: "0.82rem",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}
        >
          <div>
            <strong style={{ color: "#6ee7b7" }}>Peer-Consensus Drift Correction Active:</strong>
            <span style={{ color: "#e2e8f0", marginLeft: "0.5rem" }}>
              Baseline Median: {consensusReport.baseline_pm25_median} µg/m³ across {consensusReport.nodes_involved.length} nodes.
            </span>
          </div>
          <span className="badge" style={{ background: "rgba(16, 185, 129, 0.25)", color: "#a7f3d0" }}>
            Variance Reduced by {consensusReport.drift_variance_reduction_pct}%
          </span>
        </div>
      )}

      {/* Mesh Nodes Table */}
      {topology && (
        <div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0.75rem", marginBottom: "1rem" }}>
            {topology.nodes.map((node) => {
              const tb = getTransportBadge(node.active_transport);
              return (
                <div
                  key={node.node_id}
                  style={{
                    background: "rgba(255, 255, 255, 0.03)",
                    border: "1px solid var(--border)",
                    borderRadius: "0.75rem",
                    padding: "0.85rem",
                    display: "flex",
                    flexDirection: "column",
                    gap: "0.4rem"
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontWeight: 700, fontSize: "0.9rem", color: "#f8fafc" }}>{node.node_id}</span>
                    <span className="badge" style={{ background: tb.bg, color: tb.color, fontSize: "0.7rem" }}>
                      {tb.label}
                    </span>
                  </div>

                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                    MAC: <code>{node.mac_address}</code>
                  </div>

                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", marginTop: "0.2rem" }}>
                    <span>Role: <strong style={{ color: "#cbd5e1" }}>{node.role}</strong></span>
                    <span>Hops: <strong style={{ color: "#38bdf8" }}>{node.hop_count}</strong></span>
                  </div>

                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem" }}>
                    <span>RSSI: <strong style={{ color: node.rssi_dbm > -65 ? "#4ade80" : "#facc15" }}>{node.rssi_dbm} dBm</strong></span>
                    <span style={{ display: "flex", alignItems: "center", gap: "0.2rem" }}>
                      <Battery size={13} color="#4ade80" /> {node.battery_pct}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Active Peer Routes */}
          <div style={{ background: "rgba(0,0,0,0.2)", borderRadius: "0.75rem", padding: "0.85rem", border: "1px solid var(--border)" }}>
            <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "#94a3b8", marginBottom: "0.5rem" }}>
              Active Swarm Mesh Telemetry Relay Routes (Zero-Infrastructure Ad-Hoc Routing)
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
              {topology.routes.map((rt, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    fontSize: "0.78rem",
                    padding: "0.35rem 0.6rem",
                    background: "rgba(255,255,255,0.02)",
                    borderRadius: "0.4rem"
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <span style={{ fontWeight: 600, color: "#e2e8f0" }}>{rt.from}</span>
                    <ArrowRight size={13} color="var(--text-muted)" />
                    <span style={{ fontWeight: 600, color: "#a5b4fc" }}>{rt.to}</span>
                    <span className="badge" style={{ fontSize: "0.68rem", background: "rgba(255,255,255,0.06)" }}>{rt.transport}</span>
                  </div>
                  <span style={{ color: "#4ade80", fontSize: "0.75rem" }}>Link Quality: {rt.lq_pct}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
