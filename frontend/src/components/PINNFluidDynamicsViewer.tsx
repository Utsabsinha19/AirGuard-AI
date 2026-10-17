import React, { useState, useEffect } from "react";
import {
  Wind,
  Activity,
  Layers,
  Compass,
  Building2,
  Sliders,
  CheckCircle2,
  RefreshCw,
  Zap,
  Target
} from "lucide-react";
import type { PINNSimulationResult, StreetCanyonResult } from "../types";
import { runPINN3DSimulation, runPINNStreetCanyon } from "../api";

export const PINNFluidDynamicsViewer: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"indoor" | "canyon">("indoor");
  const [loading, setLoading] = useState(false);

  // Indoor PINN State
  const [indoorSim, setIndoorSim] = useState<PINNSimulationResult | null>(null);
  const [inletVel, setInletVel] = useState<number>(1.5);
  const [exhaustCfm, setExhaustCfm] = useState<number>(240);
  const [emissionSource, setEmissionSource] = useState<number>(35);

  // Street Canyon State
  const [canyonSim, setCanyonSim] = useState<StreetCanyonResult | null>(null);
  const [bldHeight, setBldHeight] = useState<number>(28);
  const [streetWidth, setStreetWidth] = useState<number>(20);
  const [ambientWind, setAmbientWind] = useState<number>(4.2);

  const fetchIndoor = async () => {
    setLoading(true);
    try {
      const res = await runPINN3DSimulation({
        inlet_velocity_mps: inletVel,
        vent_exhaust_rate_cfm: exhaustCfm,
        emission_source_ug_s: emissionSource,
        resolution_x: 8,
        resolution_y: 8,
        resolution_z: 4
      });
      setIndoorSim(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchCanyon = async () => {
    setLoading(true);
    try {
      const res = await runPINNStreetCanyon({
        building_height_m: bldHeight,
        street_width_m: streetWidth,
        ambient_wind_mps: ambientWind,
        wind_direction_deg: 45,
        traffic_emissions_ug_m_s: 80
      });
      setCanyonSim(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === "indoor") fetchIndoor();
    else fetchCanyon();
  }, [activeTab]);

  return (
    <div className="card" style={{ padding: "1.25rem", borderRadius: "1rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
          <div style={{ background: "rgba(59, 130, 246, 0.15)", padding: "0.5rem", borderRadius: "0.6rem", color: "#60a5fa" }}>
            <Wind size={20} />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700 }}>PINN 3D Fluid Dynamics & Canyon Dispersion</h3>
              <span className="badge" style={{ background: "rgba(59, 130, 246, 0.2)", color: "#93c5fd" }}>
                Navier-Stokes PDE
              </span>
            </div>
            <p style={{ margin: 0, fontSize: "0.78rem", color: "var(--text-muted)" }}>
              Physics-Informed Neural Network solving 3D airflow advection, vortices, and street canyons
            </p>
          </div>
        </div>

        {/* Tab Switcher */}
        <div style={{ display: "flex", background: "rgba(255,255,255,0.05)", borderRadius: "0.5rem", padding: "0.2rem", border: "1px solid var(--border)" }}>
          <button
            className={`btn-tab ${activeTab === "indoor" ? "active" : ""}`}
            onClick={() => setActiveTab("indoor")}
            style={{
              padding: "0.35rem 0.8rem",
              fontSize: "0.8rem",
              borderRadius: "0.4rem",
              border: "none",
              background: activeTab === "indoor" ? "var(--primary, #3b82f6)" : "transparent",
              color: "#fff",
              cursor: "pointer"
            }}
          >
            Indoor 3D Room
          </button>
          <button
            className={`btn-tab ${activeTab === "canyon" ? "active" : ""}`}
            onClick={() => setActiveTab("canyon")}
            style={{
              padding: "0.35rem 0.8rem",
              fontSize: "0.8rem",
              borderRadius: "0.4rem",
              border: "none",
              background: activeTab === "canyon" ? "var(--primary, #3b82f6)" : "transparent",
              color: "#fff",
              cursor: "pointer"
            }}
          >
            Urban Street Canyon
          </button>
        </div>
      </div>

      {activeTab === "indoor" && (
        <div>
          {/* Controls */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "0.75rem", marginBottom: "1rem", background: "rgba(0,0,0,0.15)", padding: "0.75rem", borderRadius: "0.75rem" }}>
            <div>
              <label style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "block" }}>Inlet Jet Velocity: {inletVel} m/s</label>
              <input type="range" min="0.5" max="3.0" step="0.1" value={inletVel} onChange={(e) => setInletVel(parseFloat(e.target.value))} style={{ width: "100%" }} />
            </div>
            <div>
              <label style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "block" }}>Exhaust CFM: {exhaustCfm} CFM</label>
              <input type="range" min="80" max="450" step="10" value={exhaustCfm} onChange={(e) => setExhaustCfm(parseInt(e.target.value))} style={{ width: "100%" }} />
            </div>
            <div>
              <label style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "block" }}>Emission Source: {emissionSource} µg/s</label>
              <input type="range" min="10" max="100" step="5" value={emissionSource} onChange={(e) => setEmissionSource(parseInt(e.target.value))} style={{ width: "100%" }} />
            </div>
            <div style={{ display: "flex", alignItems: "flex-end" }}>
              <button className="btn btn-secondary" onClick={fetchIndoor} disabled={loading} style={{ width: "100%", padding: "0.45rem", fontSize: "0.8rem" }}>
                <RefreshCw size={14} className={loading ? "spin" : ""} style={{ marginRight: "0.4rem" }} /> Re-solve PINN
              </button>
            </div>
          </div>

          {indoorSim && (
            <div>
              {/* Metrics Grid */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "0.75rem", marginBottom: "1rem" }}>
                <div style={{ background: "rgba(255,255,255,0.03)", padding: "0.75rem", borderRadius: "0.5rem", border: "1px solid var(--border)" }}>
                  <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Navier-Stokes Residual</div>
                  <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "#38bdf8" }}>{indoorSim.navier_stokes_residual.toFixed(5)}</div>
                  <div style={{ fontSize: "0.7rem", color: "#4ade80" }}>Continuity Conserved</div>
                </div>
                <div style={{ background: "rgba(255,255,255,0.03)", padding: "0.75rem", borderRadius: "0.5rem", border: "1px solid var(--border)" }}>
                  <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Vortex Intensity</div>
                  <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "#facc15" }}>{indoorSim.vortex_intensity.toFixed(3)}</div>
                  <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Recirculation strength</div>
                </div>
                <div style={{ background: "rgba(255,255,255,0.03)", padding: "0.75rem", borderRadius: "0.5rem", border: "1px solid var(--border)" }}>
                  <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Predicted Clearance Time</div>
                  <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "#f43f5e" }}>{indoorSim.predicted_clear_time_mins} mins</div>
                  <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>To 10% peak baseline</div>
                </div>
                <div style={{ background: "rgba(255,255,255,0.03)", padding: "0.75rem", borderRadius: "0.5rem", border: "1px solid var(--border)" }}>
                  <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Optimal Purifier Position</div>
                  <div style={{ fontSize: "1.05rem", fontWeight: 700, color: "#a855f7" }}>
                    ({indoorSim.optimal_purifier_coordinates.x_m}m, {indoorSim.optimal_purifier_coordinates.y_m}m)
                  </div>
                  <div style={{ fontSize: "0.7rem", color: "#c084fc" }}>Vortex Core Max Efficiency</div>
                </div>
              </div>

              {/* 3D Grid Plan View Visualization */}
              <div style={{ background: "rgba(15, 23, 42, 0.7)", border: "1px solid var(--border)", borderRadius: "0.75rem", padding: "1rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                  <span style={{ fontSize: "0.82rem", fontWeight: 600, color: "#94a3b8" }}>
                    3D Velocity Streamlines & Pollutant Isosurfaces (Plan Slice Z = 1.2m)
                  </span>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                    Total Solved Grid Points: {indoorSim.grid_points.length}
                  </span>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(8, 1fr)", gap: "4px", padding: "0.5rem", background: "#0b1329", borderRadius: "0.5rem" }}>
                  {indoorSim.grid_points.slice(0, 64).map((pt, i) => {
                    const heat = Math.min(1, pt.concentration / 70);
                    const r = Math.round(239 * heat);
                    const g = Math.round(68 * (1 - heat) + 140 * heat);
                    const b = Math.round(68 * (1 - heat));
                    return (
                      <div
                        key={i}
                        title={`(${pt.x}m, ${pt.y}m) C: ${pt.concentration} µg/m³ | Vel: (${pt.velocity_u}, ${pt.velocity_v})`}
                        style={{
                          height: 36,
                          borderRadius: 4,
                          background: `rgb(${r}, ${g}, ${b})`,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: "0.68rem",
                          color: "#fff",
                          fontWeight: 600,
                          cursor: "pointer",
                          transition: "transform 0.15s ease"
                        }}
                      >
                        {pt.concentration > 25 ? `${Math.round(pt.concentration)}` : "·"}
                      </div>
                    );
                  })}
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.72rem", color: "var(--text-muted)", marginTop: "0.5rem" }}>
                  <span>Inlet Jet (West Wall) →</span>
                  <span>Center Room Stagnant Core</span>
                  <span>→ Exhaust Vent (East Wall)</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === "canyon" && (
        <div>
          {/* Canyon Controls */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "0.75rem", marginBottom: "1rem", background: "rgba(0,0,0,0.15)", padding: "0.75rem", borderRadius: "0.75rem" }}>
            <div>
              <label style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "block" }}>Building Height: {bldHeight} m</label>
              <input type="range" min="10" max="60" step="2" value={bldHeight} onChange={(e) => setBldHeight(parseInt(e.target.value))} style={{ width: "100%" }} />
            </div>
            <div>
              <label style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "block" }}>Street Width: {streetWidth} m</label>
              <input type="range" min="10" max="40" step="2" value={streetWidth} onChange={(e) => setStreetWidth(parseInt(e.target.value))} style={{ width: "100%" }} />
            </div>
            <div>
              <label style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "block" }}>Ambient Wind: {ambientWind} m/s</label>
              <input type="range" min="1.0" max="10.0" step="0.2" value={ambientWind} onChange={(e) => setAmbientWind(parseFloat(e.target.value))} style={{ width: "100%" }} />
            </div>
            <div style={{ display: "flex", alignItems: "flex-end" }}>
              <button className="btn btn-secondary" onClick={fetchCanyon} disabled={loading} style={{ width: "100%", padding: "0.45rem", fontSize: "0.8rem" }}>
                <RefreshCw size={14} className={loading ? "spin" : ""} style={{ marginRight: "0.4rem" }} /> Re-solve Canyon
              </button>
            </div>
          </div>

          {canyonSim && (
            <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "1rem" }}>
              {/* Canyon Architecture Card */}
              <div style={{ background: "rgba(15, 23, 42, 0.7)", border: "1px solid var(--border)", borderRadius: "0.75rem", padding: "1rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                  <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "#38bdf8" }}>Oke Flow Regime: {canyonSim.recirculation_regime}</span>
                  <span className="badge" style={{ background: canyonSim.pedestrian_exposure_tier === "HAZARDOUS" ? "rgba(239, 68, 68, 0.2)" : "rgba(34, 197, 94, 0.2)", color: canyonSim.pedestrian_exposure_tier === "HAZARDOUS" ? "#f87171" : "#4ade80" }}>
                    {canyonSim.pedestrian_exposure_tier} Exposure
                  </span>
                </div>
                <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "1rem" }}>
                  Aspect Ratio H/W = <strong>{canyonSim.aspect_ratio}</strong>. A strong recirculating street canyon vortex ({canyonSim.canyon_vortex_rpm} RPM) traps vehicle exhaust on the leeward building face.
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
                  <div style={{ background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.3)", borderRadius: "0.5rem", padding: "0.75rem" }}>
                    <div style={{ fontSize: "0.72rem", color: "#fca5a5" }}>Leeward Wall Concentration</div>
                    <div style={{ fontSize: "1.25rem", fontWeight: 700, color: "#f87171" }}>{canyonSim.leeward_concentration_ug_m3} µg/m³</div>
                    <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Trapped vortex stagnation</div>
                  </div>
                  <div style={{ background: "rgba(34, 197, 94, 0.1)", border: "1px solid rgba(34, 197, 94, 0.3)", borderRadius: "0.5rem", padding: "0.75rem" }}>
                    <div style={{ fontSize: "0.72rem", color: "#86efac" }}>Windward Wall Concentration</div>
                    <div style={{ fontSize: "1.25rem", fontWeight: 700, color: "#4ade80" }}>{canyonSim.windward_concentration_ug_m3} µg/m³</div>
                    <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Ventilated by downdraft</div>
                  </div>
                </div>
              </div>

              {/* Building Infiltration Advice */}
              <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)", borderRadius: "0.75rem", padding: "1rem", fontSize: "0.82rem" }}>
                <strong style={{ color: "#facc15" }}>Building Envelope Intervention:</strong>
                <p style={{ color: "var(--text-muted)", marginTop: "0.3rem" }}>
                  Because street canyon vortex traps {canyonSim.leeward_concentration_ug_m3} µg/m³ on the leeward facade, AirGuard has dynamically adjusted HVAC intake:
                </p>
                <ul style={{ paddingLeft: "1.2rem", margin: "0.5rem 0", color: "#cbd5e1" }}>
                  <li>Shift fresh air intake to windward rooftop intake louvers.</li>
                  <li>Engage motorized window interlocks on lower 5 floors.</li>
                  <li>Adjust VAV positive pressurization to prevent street-level infiltration.</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
