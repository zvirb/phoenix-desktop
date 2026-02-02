import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import "./App.css";

function App() {
  const [status, setStatus] = useState("Connecting...");
  const [activeTime, setActiveTime] = useState(0);
  const [isAgent, setIsAgent] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [token, setToken] = useState<string | null>(null);
  const [apiUrl, setApiUrl] = useState<string>("http://localhost:8000"); // Default
  const [subtasks, setSubtasks] = useState<string[]>([]);
  const [currentWindow, setCurrentWindow] = useState("Unknown");

  useEffect(() => {
    const unlistenPromise = listen<string>('telemetry', (event) => {
      try {
        const payload = JSON.parse(event.payload);

        if (payload.event !== "context_update") {
          setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${payload.event}`, ...prev].slice(0, 5));
        }

        if (payload.event === "context_update") {
          setStatus(payload.payload.status);
          setActiveTime(payload.payload.active_time_seconds);
          setIsAgent(payload.payload.is_agent_activity);
          setCurrentWindow(payload.payload.current_window || "Unknown");
        } else if (payload.event === "ready") {
          setStatus("Connected");
          if (payload.payload.token) {
            setToken(payload.payload.token);
            setLogs(prev => ["Token received", ...prev]);
          }
        }
      } catch (e) {
        console.error("Failed to parse telemetry:", e);
      }
    });

    return () => {
      unlistenPromise.then(unlisten => unlisten());
    };
  }, []);

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // ... existing effect ...
    const unlistenPromise = listen<string>('telemetry', (event) => {
      try {
        const payload = JSON.parse(event.payload);

        if (payload.event !== "context_update") {
          setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${payload.event}`, ...prev].slice(0, 5));
        }

        if (payload.event === "error") {
          const errMsg = typeof payload.payload === 'string'
            ? payload.payload
            : (payload.payload.message || JSON.stringify(payload.payload));
          setLogs(prev => [`Error: ${errMsg}`, ...prev]);
          setStatus("Error");
        } else if (payload.event === "context_update") {
          setStatus(payload.payload.status);
          setActiveTime(payload.payload.active_time_seconds);
          setIsAgent(payload.payload.is_agent_activity);
          setCurrentWindow(payload.payload.current_window || "Unknown");
        } else if (payload.event === "ready") {
          setStatus("Connected");
          if (payload.payload.token) {
            setToken(payload.payload.token);
            setLogs(prev => ["Token received", ...prev]);
          }
          if (payload.payload.api_url) {
            setApiUrl(payload.payload.api_url);
            setLogs(prev => [`API: ${payload.payload.api_url}`, ...prev]);
          }
        } else if (payload.event === "decomposition_result") {
          if (payload.payload.success) {
            const data = payload.payload.data;
            if (Array.isArray(data.subtasks)) {
              setSubtasks(data.subtasks);
            } else if (Array.isArray(data)) {
              setSubtasks(data);
            } else {
              setSubtasks(["Checked. No breakdown needed."]);
            }
          } else {
            setSubtasks([`Failed: ${payload.payload.error}`]);
          }
          setLoading(false);
        }
      } catch (e) {
        console.error("Failed to parse telemetry:", e);
      }
    });

    return () => {
      unlistenPromise.then(unlisten => unlisten());
    };
  }, []);

  const handleDecompose = async (text: string) => {
    if (!text.trim()) return;
    setLoading(true);
    setSubtasks([]);
    setLogs(prev => [`[Request] Decompose: ${text}`, ...prev]);

    // Send to Sidecar via Rust
    try {
      await invoke('decompose_task', { text });
    } catch (e) {
      setLogs(prev => [`Error sending command: ${e}`, ...prev]);
      setLoading(false);
    }
  };

  return (
    <main className="omnibox-container">
      <div className="search-bar">
        {/* ... (Search Bar content) ... */}
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <input
            autoFocus
            type="text"
            placeholder="What are you working on?"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                const val = e.currentTarget.value;
                handleDecompose(val);
                e.currentTarget.value = "";
              }
            }}
            style={{ flex: 1 }}
          />
          <button onClick={() => {
            invoke('trigger_capture');
            setLogs(prev => ["[Capture] Manual Trigger Sent", ...prev]);
          }}>📷</button>
        </div>
        {loading && <span style={{ marginLeft: 10 }}>Processing...</span>}
      </div>

      {subtasks.length > 0 && (
        <div className="subtasks-card" style={{
          background: '#252526',
          padding: 15,
          borderRadius: 8,
          marginBottom: 20
        }}>
          <h3>Suggested Breakdown</h3>
          <ul style={{ paddingLeft: 20 }}>
            {subtasks.map((t, i) => <li key={i}>{typeof t === 'string' ? t : JSON.stringify(t)}</li>)}
          </ul>
        </div>
      )}

      {/* Context Mirror Card */}
      <div className="context-card">
        <div className="context-header">
          <span className="context-label">CURRENT FOCUS</span>
          {isAgent && <span className="agent-badge">AI AGENT ACTIVE</span>}
        </div>
        <div className="context-body">
          <div className="window-title" title={currentWindow}>
            {currentWindow.length > 50 ? currentWindow.substring(0, 50) + "..." : currentWindow}
          </div>
          <div className="session-stats">
            <div className="stat-item">
              <span className="stat-value">{Math.floor(activeTime / 60)}m</span>
              <span className="stat-label">Session</span>
            </div>
            <div className={`stat-item ${status === 'active' ? 'active-pulse' : ''}`}>
              <span className="stat-value">{status.toUpperCase()}</span>
              <span className="stat-label">State</span>
            </div>
          </div>
        </div>
      </div>

      <div className="debug-logs">
        {logs.map((log, i) => (
          <div key={i} className="log-entry">{log}</div>
        ))}
      </div>
    </main>
  );
}

export default App;
