import { useState, useEffect, useRef } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import "./App.css";

const kbdStyle = {
  backgroundColor: '#333',
  borderRadius: '4px',
  border: '1px solid #444',
  boxShadow: '0 1px 1px rgba(0, 0, 0, 0.2), 0 2px 0 0 rgba(255, 255, 255, 0.1) inset',
  color: '#eee',
  display: 'inline-block',
  fontFamily: 'Consolas, "Liberation Mono", Menlo, Courier, monospace',
  fontSize: '0.85em',
  fontWeight: 700,
  lineHeight: 1,
  padding: '2px 5px',
  whiteSpace: 'nowrap',
} as const;

function App() {
  const [status, setStatus] = useState("Connecting...");
  const [activeTime, setActiveTime] = useState(0);
  const [isAgent, setIsAgent] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [token, setToken] = useState<string | null>(null);
  const [apiUrl, setApiUrl] = useState<string>("http://localhost:8000"); // Default
  const [subtasks, setSubtasks] = useState<string[]>([]);
  const [currentWindow, setCurrentWindow] = useState("Unknown");
  const [showSettings, setShowSettings] = useState(false);
  const [loading, setLoading] = useState(false);
  const [taskInput, setTaskInput] = useState("");
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [captureStatus, setCaptureStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const copyTimeoutRef = useRef<number | null>(null);
  const settingsBtnRef = useRef<HTMLButtonElement>(null);
  const settingsModalRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const getStatusColor = (s: string) => {
    switch (s.toLowerCase()) {
      case 'connected':
      case 'active':
        return '#4ade80';
      case 'idle':
        return '#facc15';
      case 'error':
      case 'disconnected':
        return '#ef4444';
      default:
        return '#888';
    }
  };

  const closeSettings = () => {
    setShowSettings(false);
    // Restore focus to the trigger button
    setTimeout(() => settingsBtnRef.current?.focus(), 0);
  };

  const handleCopy = (text: string, fieldId: string) => {
    navigator.clipboard.writeText(text).then(() => {
      if (copyTimeoutRef.current) {
        window.clearTimeout(copyTimeoutRef.current);
      }
      setCopiedField(fieldId);
      copyTimeoutRef.current = window.setTimeout(() => {
        setCopiedField(null);
        copyTimeoutRef.current = null;
      }, 2000);
    });
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && showSettings) {
        closeSettings();
      }
      if (e.key === '?' && !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName) && !showSettings) {
        e.preventDefault();
        setShowSettings(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [showSettings]);

  useEffect(() => {
    if (!showSettings || !settingsModalRef.current) return;
    const modal = settingsModalRef.current;

    const focusable = modal.querySelectorAll('button, input, [href], select, textarea, [tabindex]:not([tabindex="-1"])');
    if (focusable.length === 0) return;

    const first = focusable[0] as HTMLElement;
    const last = focusable[focusable.length - 1] as HTMLElement;

    const handleTab = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === first) {
            e.preventDefault();
            last.focus();
          }
        } else {
          if (document.activeElement === last) {
            e.preventDefault();
            first.focus();
          }
        }
      }
    };

    modal.addEventListener('keydown', handleTab);
    return () => modal.removeEventListener('keydown', handleTab);
  }, [showSettings]);

  useEffect(() => {
    // ... existing effect ...
    // All events from the Python sidecar are emitted as 'telemetry' events with a JSON payload
    // The payload.event field determines the specific event type (e.g., context_update, ocr_status, etc.)
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
          if (payload.payload && (payload.payload.code === 'OCR_FAIL' || payload.payload.code === 'OCR_NET_FAIL')) {
            setCaptureStatus('error');
            setTimeout(() => setCaptureStatus('idle'), 2000);
          }
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
        } else if (payload.event === "ocr_status") {
          if (payload.payload.status === "processing") {
            setCaptureStatus('loading');
          }
        } else if (payload.event === "ocr_result") {
          setCaptureStatus('success');
          setTimeout(() => setCaptureStatus('idle'), 2000);
          setLogs(prev => [`OCR: ${payload.payload.text}`, ...prev]);
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

  const handleSubmit = () => {
    if (loading) return;
    if (taskInput.trim()) {
      handleDecompose(taskInput);
      setTaskInput("");
    }
  };

  const handleCapture = async () => {
    try {
      setCaptureStatus('loading');
      await invoke('trigger_capture');
      setLogs(prev => ["[Capture] Manual Trigger Sent", ...prev]);
    } catch (e) {
      console.error(e);
      setLogs(prev => [`[Capture] Failed: ${e}`, ...prev]);
      // Ensure state is reset on error
      setCaptureStatus('error');
      setTimeout(() => setCaptureStatus('idle'), 2000);
    }
  };

  return (
    <main className="omnibox-container">
      <div className="search-bar" aria-busy={loading}>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', width: '100%' }}>
          <div style={{ position: 'relative', flex: 1, display: 'flex', alignItems: 'center' }}>
            <input
              ref={inputRef}
              autoFocus
              type="text"
              aria-label="Task description"
              value={taskInput}
              onChange={(e) => setTaskInput(e.target.value)}
              readOnly={loading}
              placeholder={loading ? "Thinking..." : "What are you working on?"}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSubmit();
                }
              }}
              style={{ width: '100%', paddingRight: '30px' }}
            />
            {taskInput && !loading && (
              <button
                className="icon-button"
                aria-label="Clear task"
                onClick={() => {
                  setTaskInput("");
                  inputRef.current?.focus();
                }}
                style={{
                  position: 'absolute',
                  right: '0',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '24px',
                  height: '24px',
                  padding: '4px',
                  color: '#666',
                  borderRadius: '50%'
                }}
              >
                <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            )}
          </div>
          <button
            className="icon-button"
            aria-label={loading ? "Processing task" : "Submit task"}
            title="Submit task"
            disabled={loading || !taskInput.trim()}
            onClick={handleSubmit}
          >
            {loading ? (
              <div className="spinner" role="status" aria-label="Processing"></div>
            ) : (
              <svg aria-hidden="true" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            )}
          </button>
          <button
            className="icon-button"
            aria-label={captureStatus === 'success' ? "Screenshot captured" : captureStatus === 'error' ? "Capture failed" : captureStatus === 'loading' ? "Capturing screenshot..." : "Capture screenshot"}
            title={captureStatus === 'success' ? "Screenshot captured" : captureStatus === 'error' ? "Capture failed" : captureStatus === 'loading' ? "Capturing screenshot..." : "Capture screenshot"}
            disabled={captureStatus === 'loading'}
            onClick={handleCapture}
            style={{ color: captureStatus === 'success' ? '#4ade80' : (captureStatus === 'error' ? '#ef4444' : 'inherit') }}
          >
            {captureStatus === 'loading' ? (
              <div className="spinner" role="status" aria-label="Capturing"></div>
            ) : captureStatus === 'success' ? (
              <svg aria-hidden="true" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            ) : captureStatus === 'error' ? (
              <svg aria-hidden="true" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
            ) : (
              <svg aria-hidden="true" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
                <circle cx="12" cy="13" r="4" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {subtasks.length > 0 && (
        <div className="subtasks-card" role="region" aria-label="Task breakdown">
          <div className="subtasks-header">
            <h3>Suggested Breakdown</h3>
            <button
              className="icon-button"
              aria-label={copiedField === 'subtasks' ? "Copied subtasks" : "Copy subtasks"}
              title={copiedField === 'subtasks' ? "Copied" : "Copy all"}
              onClick={() => handleCopy(subtasks.map(t => typeof t === 'string' ? t : JSON.stringify(t)).join('\n'), 'subtasks')}
              style={{ padding: 4, width: 28, height: 28, color: copiedField === 'subtasks' ? '#4ade80' : 'inherit' }}
            >
              {copiedField === 'subtasks' ? (
                <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              ) : (
                <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
              )}
            </button>
          </div>
          <ul className="subtasks-list">
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
            {currentWindow}
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

      {/* Settings Panel */}
      <div style={{ position: 'fixed', bottom: 10, right: 10 }}>
        <button
          ref={settingsBtnRef}
          className="icon-button"
          aria-label="Open settings (Shift+/)"
          aria-haspopup="dialog"
          aria-expanded={showSettings}
          title="Open settings (Shift+/)"
          onClick={() => setShowSettings(!showSettings)}
          style={{ background: '#252526', border: '1px solid #333' }}
        >
          <svg aria-hidden="true" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1.51 1H15.6a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
        </button>
      </div>

      {showSettings && (
        <div
          className="settings-backdrop"
          onClick={(e) => { if (e.target === e.currentTarget) closeSettings(); }}
        >
          <div
            ref={settingsModalRef}
            role="dialog"
            aria-modal="true"
            aria-labelledby="settings-title"
            className="settings-modal"
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 id="settings-title" style={{ margin: 0, fontSize: '18px' }}>Settings</h2>
              <button
                autoFocus
                className="icon-button"
                aria-label="Close settings"
                onClick={closeSettings}
              >
                <svg aria-hidden="true" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>

            <div className="setting-item">
              <label htmlFor="settings-api-url">API URL</label>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <input id="settings-api-url" type="text" value={apiUrl} readOnly style={{ flex: 1, padding: 8, background: '#333', border: 'none', color: '#fff', borderRadius: '4px' }} />
                <button
                  className="icon-button"
                  aria-label={copiedField === 'api-url' ? "Copied API URL" : "Copy API URL"}
                  title={copiedField === 'api-url' ? "Copied API URL" : "Copy API URL"}
                  onClick={() => handleCopy(apiUrl, 'api-url')}
                  style={{ color: copiedField === 'api-url' ? '#4ade80' : 'inherit' }}
                >
                  {copiedField === 'api-url' ? (
                    <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                  ) : (
                    <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
                  )}
                </button>
              </div>
              <small>Defined in Windows Registry</small>
            </div>

            <div className="setting-item">
              <label htmlFor="settings-device-token">Device Token (Masked)</label>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <input id="settings-device-token" type="text" value={token ? `${token.substring(0, 8)}...` : "Not Loaded"} readOnly style={{ flex: 1, padding: 8, background: '#333', border: 'none', color: '#fff', borderRadius: '4px' }} />
                <button
                  className="icon-button"
                  aria-label={copiedField === 'token' ? "Copied Device Token" : "Copy Device Token"}
                  title={copiedField === 'token' ? "Copied Device Token" : "Copy Device Token"}
                  disabled={!token}
                  onClick={() => token && handleCopy(token, 'token')}
                  style={{ color: copiedField === 'token' ? '#4ade80' : 'inherit' }}
                >
                  {copiedField === 'token' ? (
                    <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                  ) : (
                    <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
                  )}
                </button>
              </div>
              <small>Stored in Windows Credential Manager</small>
            </div>

            <div className="setting-item">
              <label>Status</label>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div style={{
                  width: 8, height: 8, borderRadius: '50%',
                  background: getStatusColor(status),
                  boxShadow: `0 0 8px ${getStatusColor(status)}`
                }}></div>
                <span style={{ color: getStatusColor(status) }}>
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </span>
              </div>
            </div>

            <div style={{ marginTop: 10, textAlign: 'center', fontSize: '12px', color: '#666' }}>
              Press <kbd style={kbdStyle}>Esc</kbd> to close
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

export default App;
