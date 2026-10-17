import React, { useState, useEffect } from "react";
import {
  Sparkles,
  Bot,
  Send,
  X,
  ShieldAlert,
  Clock,
  CheckCircle2,
  BookOpen,
  Volume2,
  RefreshCw,
  Cpu
} from "lucide-react";
import type { CopilotResponse, CopilotIncidentAdvisory, Telemetry } from "../types";
import { queryCopilotAgent, fetchCopilotAdvisory } from "../api";

interface AirGuardCopilotModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedDeviceId: string;
  selectedRoom: string;
  latestTelemetry?: Telemetry;
}

export const AirGuardCopilotModal: React.FC<AirGuardCopilotModalProps> = ({
  isOpen,
  onClose,
  selectedDeviceId,
  selectedRoom,
  latestTelemetry
}) => {
  const [messages, setMessages] = useState<
    Array<{ sender: "user" | "copilot"; text: string; details?: CopilotResponse; timestamp: string }>
  >([
    {
      sender: "copilot",
      text: `Hello! I am your **AirGuard Agent** Copilot (SLM-3B-EnvHealth). I actively supervise ${selectedRoom} (${selectedDeviceId}). How can I assist you with your indoor environmental health or smart grid actuation today?`,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    }
  ]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [advisory, setAdvisory] = useState<CopilotIncidentAdvisory | null>(null);

  useEffect(() => {
    if (isOpen) {
      const code = latestTelemetry?.diagnosis?.root_cause_code || "CLEAN_STABLE";
      fetchCopilotAdvisory(selectedDeviceId, code, selectedRoom)
        .then(setAdvisory)
        .catch(() => {});
    }
  }, [isOpen, selectedDeviceId, selectedRoom, latestTelemetry]);

  if (!isOpen) return null;

  const quickQuestions = [
    "What is my air quality right now?",
    "Why is air quality getting worse?",
    "Will this trigger my asthma?",
    "How does grid tariff affect purification?"
  ];

  const handleSend = async (queryToSend?: string) => {
    const q = queryToSend || inputText;
    if (!q.trim() || loading) return;

    const userMsg = {
      sender: "user" as const,
      text: q,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    };
    setMessages((prev) => [...prev, userMsg]);
    setInputText("");
    setLoading(true);

    try {
      const res = await queryCopilotAgent(q, selectedDeviceId);
      const copilotMsg = {
        sender: "copilot" as const,
        text: res.response,
        details: res,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      };
      setMessages((prev) => [...prev, copilotMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          sender: "copilot",
          text: "I experienced a brief latency connecting to the cloud SLM. Your edge node continues local closed-loop actuation.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: 840, width: "95%", height: "85vh", display: "flex", flexDirection: "column" }}>
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border)", paddingBottom: "1rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <div style={{ background: "linear-gradient(135deg, #6366f1, #a855f7)", padding: "0.6rem", borderRadius: "0.75rem", color: "#fff", display: "flex" }}>
              <Bot size={24} />
            </div>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <h2 style={{ margin: 0, fontSize: "1.25rem", fontWeight: 700 }}>AirGuard Agent Copilot</h2>
                <span className="badge" style={{ background: "rgba(99, 102, 241, 0.2)", color: "#a5b4fc", border: "1px solid rgba(99, 102, 241, 0.4)" }}>
                  SLM-3B Edge
                </span>
                <span className="badge" style={{ background: "rgba(16, 185, 129, 0.2)", color: "#6ee7b7" }}>
                  Active Supervision
                </span>
              </div>
              <p style={{ margin: 0, fontSize: "0.82rem", color: "var(--text-muted)" }}>
                Generative environmental intelligence, multi-modal diagnosis & proactive health guidance
              </p>
            </div>
          </div>
          <button className="icon-btn" onClick={onClose} style={{ color: "var(--text-muted)" }}>
            <X size={20} />
          </button>
        </div>

        {/* Real-time Proactive Advisory Banner */}
        {advisory && advisory.incident_code !== "NOMINAL_ATMOSPHERE" && (
          <div
            style={{
              margin: "1rem 0 0.5rem 0",
              padding: "0.85rem 1rem",
              borderRadius: "0.75rem",
              background: "rgba(239, 68, 68, 0.12)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              display: "flex",
              alignItems: "flex-start",
              gap: "0.75rem"
            }}
          >
            <ShieldAlert size={20} color="#f87171" style={{ flexShrink: 0, marginTop: "0.15rem" }} />
            <div style={{ flex: 1, fontSize: "0.85rem" }}>
              <div style={{ fontWeight: 600, color: "#fca5a5", display: "flex", justifyContent: "space-between" }}>
                <span>PROACTIVE ADVISORY: {advisory.incident_code}</span>
                {advisory.estimated_clear_time_mins && (
                  <span style={{ display: "flex", alignItems: "center", gap: "0.3rem", color: "#fef08a" }}>
                    <Clock size={13} /> Clear Est: {advisory.estimated_clear_time_mins} mins
                  </span>
                )}
              </div>
              <div style={{ color: "#e2e8f0", marginTop: "0.25rem" }}>{advisory.plain_language_advisory}</div>
              <div style={{ color: "#93c5fd", marginTop: "0.3rem", fontSize: "0.8rem" }}>
                <strong>Automated Action:</strong> {advisory.automated_action_taken}
              </div>
            </div>
          </div>
        )}

        {/* Chat Stream Window */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            margin: "0.75rem 0",
            padding: "0.5rem",
            display: "flex",
            flexDirection: "column",
            gap: "1rem"
          }}
        >
          {messages.map((m, idx) => (
            <div
              key={idx}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: m.sender === "user" ? "flex-end" : "flex-start",
                width: "100%"
              }}
            >
              <div
                style={{
                  maxWidth: "85%",
                  padding: "0.85rem 1.1rem",
                  borderRadius: m.sender === "user" ? "1rem 1rem 0.2rem 1rem" : "1rem 1rem 1rem 0.2rem",
                  background: m.sender === "user" ? "linear-gradient(135deg, #4f46e5, #4338ca)" : "var(--card-bg, #1e293b)",
                  border: m.sender === "user" ? "none" : "1px solid var(--border)",
                  color: "#f8fafc",
                  fontSize: "0.9rem",
                  lineHeight: 1.5,
                  boxShadow: "0 4px 12px rgba(0,0,0,0.15)"
                }}
              >
                <div style={{ whiteSpace: "pre-wrap" }}>{m.text}</div>

                {m.details && (
                  <div style={{ marginTop: "0.75rem", borderTop: "1px solid rgba(255,255,255,0.1)", paddingTop: "0.5rem", fontSize: "0.8rem" }}>
                    {m.details.recommended_actions?.length > 0 && (
                      <div style={{ marginTop: "0.4rem" }}>
                        <strong style={{ color: "#6ee7b7" }}>Recommended Interventions:</strong>
                        <ul style={{ margin: "0.25rem 0 0 1rem", padding: 0 }}>
                          {m.details.recommended_actions.map((act, i) => (
                            <li key={i} style={{ color: "#cbd5e1" }}>{act}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {m.details.citations?.length > 0 && (
                      <div style={{ marginTop: "0.5rem", color: "#94a3b8", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                        <BookOpen size={13} /> Citations: {m.details.citations.join(" | ")}
                      </div>
                    )}
                  </div>
                )}
              </div>
              <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "0.2rem", marginInline: "0.4rem" }}>
                {m.timestamp}
              </span>
            </div>
          ))}
          {loading && (
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", color: "var(--text-muted)", fontSize: "0.85rem" }}>
              <RefreshCw className="spin" size={16} /> AirGuard Agent is reasoning over timeseries and multi-sensor matrices...
            </div>
          )}
        </div>

        {/* Quick Suggestion Chips */}
        <div style={{ display: "flex", gap: "0.5rem", overflowX: "auto", paddingBottom: "0.5rem" }}>
          {quickQuestions.map((q, i) => (
            <button
              key={i}
              className="badge"
              onClick={() => handleSend(q)}
              style={{
                cursor: "pointer",
                background: "rgba(255,255,255,0.06)",
                border: "1px solid var(--border)",
                color: "#e2e8f0",
                fontSize: "0.78rem",
                padding: "0.4rem 0.75rem",
                whiteSpace: "nowrap"
              }}
            >
              <Sparkles size={12} style={{ marginRight: "0.3rem", color: "#c084fc" }} /> {q}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div style={{ display: "flex", gap: "0.5rem", paddingTop: "0.5rem", borderTop: "1px solid var(--border)" }}>
          <input
            type="text"
            className="input-field"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask AirGuard Agent about air quality root causes, health exposure, or ventilation..."
            style={{ flex: 1, padding: "0.75rem 1rem", borderRadius: "0.75rem" }}
          />
          <button
            className="btn btn-primary"
            onClick={() => handleSend()}
            disabled={loading || !inputText.trim()}
            style={{ display: "flex", alignItems: "center", gap: "0.4rem", padding: "0 1.25rem", borderRadius: "0.75rem" }}
          >
            <Send size={16} /> Send
          </button>
        </div>
      </div>
    </div>
  );
};
