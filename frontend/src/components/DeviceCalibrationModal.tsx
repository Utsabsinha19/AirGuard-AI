import React, { useState } from "react";
import type { Device } from "../types";
import { Sliders, X, Check, RotateCcw } from "lucide-react";
import { calibrateDevice } from "../api";

interface DeviceCalibrationModalProps {
  device: Device | null;
  isOpen: boolean;
  onClose: () => void;
  onCalibrationSaved: (updated: Device) => void;
}

export const DeviceCalibrationModal: React.FC<DeviceCalibrationModalProps> = ({
  device,
  isOpen,
  onClose,
  onCalibrationSaved,
}) => {
  const [pmZero, setPmZero] = useState<number>(device?.pm_zero_offset ?? 0.0);
  const [pmGain, setPmGain] = useState<number>(device?.pm_gain ?? 1.0);
  const [vocZero, setVocZero] = useState<number>(device?.voc_zero_offset ?? 0.0);
  const [vocGain, setVocGain] = useState<number>(device?.voc_gain ?? 1.0);
  const [saving, setSaving] = useState(false);

  if (!isOpen || !device) return null;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const updated = await calibrateDevice(device.id, {
        pm_zero_offset: pmZero,
        pm_gain: pmGain,
        voc_zero_offset: vocZero,
        voc_gain: vocGain,
      });
      onCalibrationSaved(updated);
      onClose();
    } catch (err: any) {
      alert(`Calibration failed: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleAutoZero = () => {
    // Uses current raw value as zero baseline
    const curPm = device.latest_telemetry?.pm2_5 ?? 5.0;
    const curVoc = device.latest_telemetry?.voc ?? 50.0;
    setPmZero(Math.max(0, curPm - 2.0));
    setVocZero(Math.max(0, curVoc - 15.0));
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="glass-panel"
        style={{ width: "100%", maxWidth: "480px", padding: "26px", borderRadius: "20px" }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <Sliders size={22} color="#38bdf8" />
            <div>
              <h3 style={{ fontSize: "18px", fontWeight: "700", color: "#ffffff" }}>
                Sensor Calibration Settings (Section 2.2)
              </h3>
              <p style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                Zero-point baseline shift and non-linear gain tuning for {device.name}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer" }}
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSave} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          
          {/* PM2.5 Calibration */}
          <div style={{ background: "rgba(255, 255, 255, 0.03)", padding: "14px", borderRadius: "12px" }}>
            <h4 style={{ fontSize: "13px", fontWeight: "700", color: "#38bdf8", marginBottom: "10px" }}>
              PMS5003 Laser Particulate Tuning
            </h4>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div>
                <label style={{ fontSize: "11px", color: "var(--text-muted)", display: "block", marginBottom: "4px" }}>
                  Zero Offset (µg/m³):
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={pmZero}
                  onChange={(e) => setPmZero(parseFloat(e.target.value) || 0)}
                  style={{
                    width: "100%",
                    background: "rgba(15, 23, 42, 0.8)",
                    border: "1px solid rgba(255, 255, 255, 0.12)",
                    borderRadius: "8px",
                    padding: "8px 10px",
                    color: "#ffffff",
                    fontSize: "12px"
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: "11px", color: "var(--text-muted)", display: "block", marginBottom: "4px" }}>
                  Gain Multiplier:
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={pmGain}
                  onChange={(e) => setPmGain(parseFloat(e.target.value) || 1.0)}
                  style={{
                    width: "100%",
                    background: "rgba(15, 23, 42, 0.8)",
                    border: "1px solid rgba(255, 255, 255, 0.12)",
                    borderRadius: "8px",
                    padding: "8px 10px",
                    color: "#ffffff",
                    fontSize: "12px"
                  }}
                />
              </div>
            </div>
          </div>

          {/* SGP30 VOC Calibration */}
          <div style={{ background: "rgba(255, 255, 255, 0.03)", padding: "14px", borderRadius: "12px" }}>
            <h4 style={{ fontSize: "13px", fontWeight: "700", color: "#ec4899", marginBottom: "10px" }}>
              SGP30 MOX Array Drift Compensation
            </h4>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div>
                <label style={{ fontSize: "11px", color: "var(--text-muted)", display: "block", marginBottom: "4px" }}>
                  Zero Offset (ppb):
                </label>
                <input
                  type="number"
                  step="1"
                  value={vocZero}
                  onChange={(e) => setVocZero(parseFloat(e.target.value) || 0)}
                  style={{
                    width: "100%",
                    background: "rgba(15, 23, 42, 0.8)",
                    border: "1px solid rgba(255, 255, 255, 0.12)",
                    borderRadius: "8px",
                    padding: "8px 10px",
                    color: "#ffffff",
                    fontSize: "12px"
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: "11px", color: "var(--text-muted)", display: "block", marginBottom: "4px" }}>
                  Sensitivity Gain:
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={vocGain}
                  onChange={(e) => setVocGain(parseFloat(e.target.value) || 1.0)}
                  style={{
                    width: "100%",
                    background: "rgba(15, 23, 42, 0.8)",
                    border: "1px solid rgba(255, 255, 255, 0.12)",
                    borderRadius: "8px",
                    padding: "8px 10px",
                    color: "#ffffff",
                    fontSize: "12px"
                  }}
                />
              </div>
            </div>
          </div>

          {/* Quick Zero & Actions */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "6px" }}>
            <button
              type="button"
              onClick={handleAutoZero}
              className="btn-secondary"
              style={{ fontSize: "11px", padding: "6px 10px" }}
            >
              <RotateCcw size={12} />
              <span>Auto-Zero Baseline</span>
            </button>

            <div style={{ display: "flex", gap: "8px" }}>
              <button type="button" onClick={onClose} className="btn-secondary">
                Cancel
              </button>
              <button type="submit" disabled={saving} className="btn-primary">
                {saving ? "Saving..." : "Apply Calibration"}
              </button>
            </div>
          </div>

        </form>
      </div>
    </div>
  );
};
