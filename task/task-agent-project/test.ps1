# create-taskagent-ui.ps1
# Run this in PowerShell to generate a small React-based UI (no npm required).
# After running: start your Python server, then open http://127.0.0.1:8000/taskagent-ui/index.html

$uiDir = Join-Path -Path (Get-Location) -ChildPath "taskagent-ui"
if (-not (Test-Path $uiDir)) { New-Item -ItemType Directory -Path $uiDir | Out-Null }

# index.html (loads React from CDN and app.js)
$indexHtml = @"
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>TaskAgent Logs UI</title>
  <link rel="stylesheet" href="./styles.css" />
</head>
<body>
  <div id="root"></div>

  <!-- React & ReactDOM (UMD builds via CDN) -->
  <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>

  <!-- App script -->
  <script src="./app.js"></script>
</body>
</html>
"@
$indexHtmlPath = Join-Path $uiDir "index.html"
$indexHtml | Out-File -FilePath $indexHtmlPath -Encoding utf8 -Force

# styles.css
$styles = @"
:root{
  --bg: #0f1724;
  --panel: #0b1220;
  --muted: #9aa4b2;
  --info: #60a5fa;
  --warn: #f59e0b;
  --error: #ef4444;
  --text: #e6eef6;
}
*{box-sizing:border-box}
body{
  margin:0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
  background: linear-gradient(180deg,#071029 0%,#0b1220 100%);
  color:var(--text);
  -webkit-font-smoothing:antialiased;
  -moz-osx-font-smoothing:grayscale;
  padding:16px;
}
.container{
  max-width:1100px;
  margin:0 auto;
}
.header{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  margin-bottom:12px;
}
.brand{font-weight:700; font-size:18px}
.controls{display:flex; gap:8px; align-items:center}
.btn{
  background:transparent;
  border:1px solid rgba(255,255,255,0.07);
  padding:8px 10px;
  border-radius:8px;
  color:var(--text);
  cursor:pointer;
}
.btn:active{transform:translateY(1px)}
.status{
  font-size:13px;
  padding:6px 8px;
  border-radius:8px;
}
.log-panel{
  background:var(--panel);
  border-radius:12px;
  padding:12px;
  height:70vh;
  overflow:auto;
  box-shadow: 0 6px 20px rgba(2,6,23,0.6);
}
.log-entry{
  padding:8px 10px;
  border-radius:8px;
  margin-bottom:8px;
  display:flex;
  gap:12px;
  align-items:flex-start;
  font-family:monospace;
  font-size:13px;
  white-space:pre-wrap;
}
.log-meta{min-width:220px; font-size:12px; color:var(--muted)}
.level-badge{display:inline-block; padding:4px 8px; border-radius:999px; font-size:12px}
.message{flex:1; color:var(--text)}
.empty{color:var(--muted); text-align:center; padding:16px}
.footer{margin-top:8px; font-size:13px; color:var(--muted)}
"@
$stylesPath = Join-Path $uiDir "styles.css"
$styles | Out-File -FilePath $stylesPath -Encoding utf8 -Force

# app.js - React application (UMD style)
$appJs = @"
(() => {
  const e = React.createElement;
  const { useState, useEffect, useRef } = React;

  // Edit this if your WS server is on a different host/port.
  const WS_URL = "ws://127.0.0.1:8765";

  function levelColor(level) {
    if (!level) return "var(--muted)";
    const l = level.toLowerCase();
    if (l.includes("error")) return "var(--error)";
    if (l.includes("warn") || l.includes("warning")) return "var(--warn)";
    if (l.includes("info")) return "var(--info)";
    return "var(--muted)";
  }

  function formatLocal(isoTs) {
    try {
      const dt = new Date(isoTs);
      if (isNaN(dt)) return isoTs;
      return dt.toLocaleString();
    } catch (err) {
      return isoTs;
    }
  }

  function useWebSocket(url, handlers) {
    const [status, setStatus] = useState("disconnected");
    const wsRef = useRef(null);
    const backoffRef = useRef(1000);
    const timeoutRef = useRef(null);

    useEffect(() => {
      let closedByUs = false;

      function connect() {
        setStatus("connecting");
        try {
          const ws = new WebSocket(url);
          wsRef.current = ws;

          ws.onopen = () => {
            setStatus("open");
            backoffRef.current = 1000;
            if (handlers && handlers.onopen) handlers.onopen(ws);
          };

          ws.onmessage = (ev) => {
            if (handlers && handlers.onmessage) handlers.onmessage(ev);
          };

          ws.onclose = (ev) => {
            if (closedByUs) { setStatus("closed"); return; }
            setStatus("closed");
            // reconnect with exponential backoff
            const wait = backoffRef.current;
            backoffRef.current = Math.min(backoffRef.current * 1.8, 30000);
            timeoutRef.current = setTimeout(connect, wait);
          };

          ws.onerror = (err) => {
            if (handlers && handlers.onerror) handlers.onerror(err);
          };
        } catch (err) {
          setStatus("error");
          timeoutRef.current = setTimeout(connect, backoffRef.current);
        }
      }

      connect();

      return () => {
        closedByUs = true;
        if (timeoutRef.current) clearTimeout(timeoutRef.current);
        if (wsRef.current) wsRef.current.close();
      };
    }, [url]);

    const send = (data) => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify(data));
      }
    };

    return { send, status, wsRef };
  }

  function App() {
    const [logs, setLogs] = useState([]);
    const [sortAsc, setSortAsc] = useState(true);
    const [filterLevel, setFilterLevel] = useState("");
    const { send, status } = useWebSocket(WS_URL, {
      onmessage: (ev) => {
        try {
          const payload = JSON.parse(ev.data);
          // Accept array messages or single object
          if (Array.isArray(payload)) {
            addManyLogs(payload);
          } else if (payload && payload.timestamp) {
            addLog(payload);
          } else if (payload.response === "history" && payload.data) {
            // server returns histories for explicit request
            addManyLogs(payload.data.map(x => {
              // if historical chat/terminal entries don't include timestamp, keep current time
              if (!x.timestamp && x.response) {
                return { timestamp: new Date().toISOString(), message: (x.command ? (x.command + "\\n" + x.response) : JSON.stringify(x)), level: "info" };
              }
              return x;
            }));
          } else {
            // fallback: show raw message
            addLog({ timestamp: new Date().toISOString(), message: JSON.stringify(payload), level: "info" });
          }
        } catch (err) {
          // not JSON?
          addLog({ timestamp: new Date().toISOString(), message: ev.data, level: "info" });
        }
      }
    });

    const listRef = useRef(null);

    function addLog(item) {
      setLogs(prev => {
        const next = [...prev, normalizeLog(item)];
        return sortAsc ? next.sort(byTimestamp) : next.sort(byTimestampDesc);
      });
    }
    function addManyLogs(items) {
      setLogs(prev => {
        const combined = [...prev, ...items.map(normalizeLog)];
        return sortAsc ? combined.sort(byTimestamp) : combined.sort(byTimestampDesc);
      });
    }

    function normalizeLog(item) {
      const ts = item.timestamp || item.time || new Date().toISOString();
      const message = item.message ?? item.msg ?? item.response ?? JSON.stringify(item);
      const level = item.level ?? "info";
      return { timestamp: ts, message: message, level: level };
    }

    function byTimestamp(a,b){ return new Date(a.timestamp) - new Date(b.timestamp) }
    function byTimestampDesc(a,b){ return new Date(b.timestamp) - new Date(a.timestamp) }

    // Auto-scroll when logs change
    useEffect(() => {
      if (listRef.current) {
        listRef.current.scrollTop = listRef.current.scrollHeight;
      }
    }, [logs]);

    function clearLogs() { setLogs([]); }

    function requestHistory(type) {
      if (send) send({ action: "get_history", type });
    }

    return e("div", { className: "container" },
      e("div", { className: "header" },
        e("div", { className: "brand" }, "TaskAgent Logs UI"),
        e("div", { className: "controls" },
          e("div", { className: "status", style: { border: "1px solid rgba(255,255,255,0.04)" } }, `WS: ${status}`),
          e("button", { className: "btn", onClick: () => requestHistory("terminal") }, "Get terminal history"),
          e("button", { className: "btn", onClick: () => requestHistory("chat") }, "Get chat history"),
          e("button", { className: "btn", onClick: () => setSortAsc(!sortAsc) }, sortAsc ? "Sort: Old→New" : "Sort: New→Old"),
          e("button", { className: "btn", onClick: clearLogs }, "Clear")
        )
      ),
      e("div", { ref: listRef, className: "log-panel" },
        logs.length === 0 ? e("div", { className: "empty" }, "No logs yet — connect your Python server and it will push logs here.") :
        logs
          .filter(l => !filterLevel || l.level.toLowerCase().includes(filterLevel.toLowerCase()))
          .map((log, idx) => {
            return e("div", { key: idx, className: "log-entry", title: log.message },
              e("div", { className: "log-meta" },
                e("div", null, formatLocal(log.timestamp)),
                e("div", { style: { marginTop:6 } },
                  e("span", { className: "level-badge", style: { background: levelColor(log.level), color: "#041028" } }, log.level)
                )
              ),
              e("div", { className: "message" }, log.message)
            );
          })
      ),
      e("div", { className: "footer" }, `Connected to ${WS_URL}. If logs appear out of order, toggle sort. Timestamps shown in your browser's local time.`)
    );
  }

  // Render
  const domRoot = document.getElementById("root");
  ReactDOM.createRoot(domRoot).render(React.createElement(App));
})();
"@
$appJsPath = Join-Path $uiDir "app.js"
$appJs | Out-File -FilePath $appJsPath -Encoding utf8 -Force

# Done
Write-Host "taskagent-ui created at: $uiDir"
Write-Host "Files:"
Get-ChildItem -Path $uiDir | ForEach-Object { Write-Host " - $($_.Name)" }

Write-Host ""
Write-Host "Next steps:"
Write-Host "1) Start your Python server (the one that runs the WebSocket & HTTP) in the same host."
Write-Host "2) Open this URL in your browser:"
Write-Host "   http://127.0.0.1:8000/taskagent-ui/index.html"
Write-Host "If your Python server serves a different directory, move the 'taskagent-ui' folder into the served directory."
