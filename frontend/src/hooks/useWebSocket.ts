import { useEffect, useRef, useState, useCallback } from "react";
import { Telemetry, AlertItem } from "../types";

interface UseWebSocketOptions {
  onTelemetry?: (data: Telemetry) => void;
  onAlert?: (alert: AlertItem) => void;
}

export function useWebSocket({ onTelemetry, onAlert }: UseWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastPing, setLastPing] = useState<number>(Date.now());
  const telWsRef = useRef<WebSocket | null>(null);
  const alertWsRef = useRef<WebSocket | null>(null);

  const onTelRef = useRef(onTelemetry);
  onTelRef.current = onTelemetry;

  const onAlertRef = useRef(onAlert);
  onAlertRef.current = onAlert;

  const connect = useCallback(() => {
    // 1. Connect Telemetry WebSocket
    try {
      const telWs = new WebSocket("ws://127.0.0.1:8000/ws/telemetry");
      telWsRef.current = telWs;

      telWs.onopen = () => {
        setIsConnected(true);
        setLastPing(Date.now());
      };

      telWs.onmessage = (event) => {
        setLastPing(Date.now());
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === "TELEMETRY_UPDATE" && onTelRef.current) {
            onTelRef.current(payload as Telemetry);
          }
        } catch {
          // ignore non-json
        }
      };

      telWs.onclose = () => {
        setIsConnected(false);
        setTimeout(connect, 3000);
      };

      telWs.onerror = () => {
        telWs.close();
      };
    } catch {
      setTimeout(connect, 3000);
    }

    // 2. Connect Alert WebSocket
    try {
      const alertWs = new WebSocket("ws://127.0.0.1:8000/ws/alerts");
      alertWsRef.current = alertWs;

      alertWs.onmessage = (event) => {
        try {
          const alert = JSON.parse(event.data);
          if (onAlertRef.current) {
            onAlertRef.current(alert as AlertItem);
          }
        } catch {
          // ignore
        }
      };

      alertWs.onclose = () => {
        // Will reconnect on loop
      };
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    connect();

    // Heartbeat ping loop
    const pingInterval = setInterval(() => {
      if (telWsRef.current && telWsRef.current.readyState === WebSocket.OPEN) {
        telWsRef.current.send("ping");
      }
    }, 15000);

    return () => {
      clearInterval(pingInterval);
      if (telWsRef.current) telWsRef.current.close();
      if (alertWsRef.current) alertWsRef.current.close();
    };
  }, [connect]);

  return { isConnected, lastPing };
}
