import React, { useState, useEffect, useCallback } from "react";
import type {
  Device,
  Telemetry,
  PredictionData,
  AnomalyDiagnosis,
  AlertItem,
  RemediationAction,
} from "./types";
import {
  fetchDevices,
  fetchHistory,
  fetchPredictions,
  fetchLiveDiagnosis,
  fetchAlerts,
  acknowledgeAlert,
  acknowledgeAllAlerts,
  convertAlertToAction,
  fetchActiveAction,
  logRemediationAction,
  resolveRemediationAction,
} from "./api";
import { useWebSocket } from "./hooks/useWebSocket";
import { Navbar } from "./components/Navbar";
import { LiveAQIGauge } from "./components/LiveAQIGauge";
import { SensorGrid } from "./components/SensorGrid";
import { ForecastChart } from "./components/ForecastChart";
import { RootCauseCard } from "./components/RootCauseCard";
import { MultiRoomHeatmap } from "./components/MultiRoomHeatmap";
import { ActionTracker } from "./components/ActionTracker";
import { AlertCenter } from "./components/AlertCenter";
import { SimulatorControls } from "./components/SimulatorControls";
import { SpatialFloorplan } from "./components/SpatialFloorplan";
import { ModelComparisonModal } from "./components/ModelComparisonModal";
import { DeviceCalibrationModal } from "./components/DeviceCalibrationModal";

export const App: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState<string>("AG-001");
  const [modelType, setModelType] = useState<string>("baseline");

  // Telemetry state
  const [latestTelemetryMap, setLatestTelemetryMap] = useState<Record<string, Telemetry>>({});
  const [history, setHistory] = useState<Telemetry[]>([]);
  const [predictions, setPredictions] = useState<PredictionData | null>(null);
  const [diagnosis, setDiagnosis] = useState<AnomalyDiagnosis | null>(null);
  
  // Alerts and Actions
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [activeAction, setActiveAction] = useState<RemediationAction | null>(null);
  const [actionHistory, setActionHistory] = useState<RemediationAction[]>([]);

  // Modals & Panels
  const [isAlertCenterOpen, setIsAlertCenterOpen] = useState(false);
  const [isSimulatorOpen, setIsSimulatorOpen] = useState(false);
  const [isActionModalOpen, setIsActionModalOpen] = useState(false);
  const [isModelComparisonOpen, setIsModelComparisonOpen] = useState(false);
  const [isCalibrationOpen, setIsCalibrationOpen] = useState(false);
  const [showFloorplan, setShowFloorplan] = useState(true);

  // Toast feedback
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4500);
  };

  // 1. Initial Device Fleet Fetch
  useEffect(() => {
    fetchDevices()
      .then((devs) => {
        setDevices(devs);
        if (devs.length > 0 && !selectedDeviceId) {
          setSelectedDeviceId(devs[0].id);
        }
      })
      .catch((err) => console.error("Could not fetch devices:", err));

    fetchAlerts().then(setAlerts).catch(() => {});
  }, []);

  // 2. Fetch data for selected room
  const loadRoomData = useCallback(async (devId: string, model: string) => {
    try {
      const [hist, preds, diag, act] = await Promise.all([
        fetchHistory(devId, 40).catch(() => []),
        fetchPredictions(devId, model).catch(() => null),
        fetchLiveDiagnosis(devId).catch(() => null),
        fetchActiveAction(devId).catch(() => null),
      ]);

      setHistory(hist);
      setPredictions(preds);
      setDiagnosis(diag);
      setActiveAction(act);

      if (hist.length > 0) {
        setLatestTelemetryMap((prev) => ({
          ...prev,
          [devId]: hist[hist.length - 1],
        }));
      }
    } catch (e) {
      console.error("Error loading room data:", e);
    }
  }, []);

  useEffect(() => {
    if (selectedDeviceId) {
      loadRoomData(selectedDeviceId, modelType);
    }
  }, [selectedDeviceId, modelType, loadRoomData]);

  // 3. Real-Time WebSocket Streaming Hook (Sub-second live updates NFR-1)
  const handleLiveTelemetry = useCallback(
    (tel: Telemetry) => {
      setLatestTelemetryMap((prev) => ({
        ...prev,
        [tel.device_id]: tel,
      }));

      // If current room is updated, append to history and update live cards
      if (tel.device_id === selectedDeviceId) {
        setHistory((prev) => {
          const updated = [...prev, tel];
          return updated.slice(-50);
        });

        if (tel.diagnosis) {
          setDiagnosis(tel.diagnosis);
        }

        // Periodically refresh predictions with fresh measurements
        fetchPredictions(selectedDeviceId, modelType)
          .then(setPredictions)
          .catch(() => {});
      }
    },
    [selectedDeviceId, modelType]
  );

  const handleLiveAlert = useCallback(
    (alert: AlertItem) => {
      setAlerts((prev) => [alert, ...prev]);
      showToast(`⚠️ [${alert.level}] ${alert.title}`);
    },
    []
  );

  const { isConnected } = useWebSocket({
    onTelemetry: handleLiveTelemetry,
    onAlert: handleLiveAlert,
  });

  const selectedDevice = devices.find((d) => d.id === selectedDeviceId);
  const currentTelemetry = latestTelemetryMap[selectedDeviceId] || selectedDevice?.latest_telemetry || null;

  // Handlers
  const handleAcknowledgeAlert = async (id: number) => {
    await acknowledgeAlert(id);
    setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, acknowledged: true } : a)));
  };

  const handleAcknowledgeAll = async () => {
    await acknowledgeAllAlerts();
    setAlerts((prev) => prev.map((a) => ({ ...a, acknowledged: true })));
  };

  const handleConvertAlertToAction = async (alertId: number) => {
    try {
      const act = await convertAlertToAction(alertId);
      setActiveAction(act);
      setAlerts((prev) => prev.map((a) => (a.id === alertId ? { ...a, acknowledged: true } : a)));
      setIsAlertCenterOpen(false);
      showToast(`⚡ Converted Alert #${alertId} into tracked Remediation!`);
    } catch (e: any) {
      showToast(`Error starting remediation: ${e.message}`);
    }
  };

  const handleDeviceCalibrated = (updated: Device) => {
    setDevices((prev) => prev.map((d) => (d.id === updated.id ? updated : d)));
    showToast(`Device ${updated.id} calibration parameters updated!`);
    loadRoomData(selectedDeviceId, modelType);
  };

  const handleLogAction = async (actionType: string, desc: string) => {
    const act = await logRemediationAction(selectedDeviceId, actionType, desc);
    setActiveAction(act);
    showToast(`Started tracking remediation: ${desc}`);
  };

  const handleResolveAction = async (id: number) => {
    const res = await resolveRemediationAction(id);
    setActiveAction(null);
    showToast(`Remediation completed! Measured Efficacy: ${res.efficacy_score}%`);
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      
      {/* Toast Notification Banner */}
      {toastMessage && (
        <div style={{
          position: "fixed",
          bottom: "24px",
          right: "24px",
          background: "linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%)",
          border: "1px solid #6366f1",
          borderRadius: "14px",
          padding: "14px 20px",
          color: "#f8fafc",
          fontSize: "13px",
          fontWeight: "600",
          boxShadow: "0 10px 30px rgba(0, 0, 0, 0.5)",
          zIndex: 100,
          animation: "slideIn 0.3s ease"
        }}>
          {toastMessage}
        </div>
      )}

      {/* Top Navbar */}
      <Navbar
        devices={devices}
        selectedDeviceId={selectedDeviceId}
        onSelectDevice={setSelectedDeviceId}
        isConnected={isConnected}
        modelType={modelType}
        onSelectModel={(m) => setModelType(m)}
        alerts={alerts}
        onOpenAlerts={() => setIsAlertCenterOpen(true)}
        onOpenSimulator={() => setIsSimulatorOpen(true)}
        onOpenActionModal={() => setIsActionModalOpen(true)}
        onOpenModelComparison={() => setIsModelComparisonOpen(true)}
        onOpenCalibration={() => setIsCalibrationOpen(true)}
        showFloorplan={showFloorplan}
        onToggleFloorplan={() => setShowFloorplan((v) => !v)}
      />

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: "0 24px 32px 24px", maxWidth: "1440px", margin: "0 auto", width: "100%" }}>
        
        {/* Active Remediation Tracker */}
        <ActionTracker
          activeAction={activeAction}
          actionHistory={actionHistory}
          onLogAction={handleLogAction}
          onResolveAction={handleResolveAction}
          isOpenModal={isActionModalOpen}
          onCloseModal={() => setIsActionModalOpen(false)}
        />

        {/* 2D Interactive Blueprint Spatial Floorplan (Toggleable) */}
        {showFloorplan && (
          <SpatialFloorplan
            devices={devices}
            selectedDeviceId={selectedDeviceId}
            onSelectDevice={setSelectedDeviceId}
            latestTelemetryMap={latestTelemetryMap}
          />
        )}

        {/* Top Split: Live AQI Gauge (Left) + Sensor Metrics Grid (Right) */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
          gap: "20px",
          marginBottom: "20px"
        }}>
          <div style={{ flex: "1 1 340px", maxWidth: "420px" }}>
            <LiveAQIGauge
              telemetry={currentTelemetry}
              roomName={selectedDevice?.room ?? "Selected Room"}
            />
          </div>

          <div style={{ flex: "2 1 600px" }}>
            <SensorGrid telemetry={currentTelemetry} />
          </div>
        </div>

        {/* Middle Split: Root Cause Diagnosis (Left) + Multi-Horizon Forecast Chart (Right) */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))",
          gap: "20px",
          marginBottom: "20px"
        }}>
          <RootCauseCard
            diagnosis={diagnosis}
            onTakeAction={() => setIsActionModalOpen(true)}
          />

          <ForecastChart
            history={history}
            predictions={predictions}
            modelType={modelType}
          />
        </div>

        {/* Multi-Room Spatial Zone Heatmap Grid */}
        <div style={{ marginBottom: "20px" }}>
          <MultiRoomHeatmap
            devices={devices}
            selectedDeviceId={selectedDeviceId}
            onSelectDevice={setSelectedDeviceId}
            latestTelemetryMap={latestTelemetryMap}
          />
        </div>

      </main>

      {/* Modals & Drawers */}
      <AlertCenter
        alerts={alerts}
        isOpen={isAlertCenterOpen}
        onClose={() => setIsAlertCenterOpen(false)}
        onAcknowledge={handleAcknowledgeAlert}
        onAcknowledgeAll={handleAcknowledgeAll}
        onConvertToAction={handleConvertAlertToAction}
      />

      <SimulatorControls
        isOpen={isSimulatorOpen}
        onClose={() => setIsSimulatorOpen(false)}
        selectedDeviceId={selectedDeviceId}
        onScenarioTriggered={(msg) => {
          showToast(msg);
          loadRoomData(selectedDeviceId, modelType);
        }}
      />

      <ModelComparisonModal
        deviceId={selectedDeviceId}
        isOpen={isModelComparisonOpen}
        onClose={() => setIsModelComparisonOpen(false)}
      />

      <DeviceCalibrationModal
        device={selectedDevice || null}
        isOpen={isCalibrationOpen}
        onClose={() => setIsCalibrationOpen(false)}
        onCalibrationSaved={handleDeviceCalibrated}
      />

    </div>
  );
};

export default App;
