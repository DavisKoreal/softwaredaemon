(() => {
  const e = React.createElement;
  const { useState, useEffect, useRef } = React;

  // Adjust if your WS server changes port
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
    } catch {
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
            handlers?.onopen?.(ws);
          };

          ws.onmessage = (ev) => {
            handlers?.onmessage?.(ev);
          };

          ws.onclose = () => {
            if (closedByUs) {
              setStatus("closed");
              return;
            }
            setStatus("closed");
            const wait = backoffRef.current;
            backoffRef.current = Math.min(backoffRef.current * 1.8, 30000);
            timeoutRef.current = setTimeout(connect, wait);
          };

          ws.onerror = (err) => {
            handlers?.onerror?.(err);
          };
        } catch {
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
    const [taskInput, setTaskInput] = useState("");
    const [lastResponse, setLastResponse] = useState("");
    const { send, status } = useWebSocket(WS_URL, {
      onmessage: (ev) => {
        try {
          const payload = JSON.parse(ev.data);
          if (payload.response === "task_submitted") {
            setLastResponse(`Task submitted: ${payload.task}`);
          } else if (payload.response === "history" && payload.data) {
            addManyLogs(
              payload.data.map((x) => ({
                timestamp: new Date().toISOString(),
                message: x.command
                  ? x.command + "\\n" + x.response
                  : JSON.stringify(x),
                level: "info",
              }))
            );
          } else if (payload.timestamp) {
            addLog(payload);
          } else {
            addLog({
              timestamp: new Date().toISOString(),
              message: JSON.stringify(payload),
              level: "info",
            });
          }
        } catch {
          addLog({
            timestamp: new Date().toISOString(),
            message: ev.data,
            level: "info",
          });
        }
      },
    });

    const listRef = useRef(null);

    function addLog(item) {
      setLogs((prev) => {
        const next = [...prev, normalizeLog(item)];
        return sortAsc ? next.sort(byTimestamp) : next.sort(byTimestampDesc);
      });
    }

    function addManyLogs(items) {
      setLogs((prev) => {
        const combined = [...prev, ...items.map(normalizeLog)];
        return sortAsc ? combined.sort(byTimestamp) : combined.sort(byTimestampDesc);
      });
    }

    function normalizeLog(item) {
      const ts = item.timestamp || new Date().toISOString();
      const message = item.message ?? item.response ?? JSON.stringify(item);
      const level = item.level ?? "info";
      return { timestamp: ts, message, level };
    }

    function byTimestamp(a, b) {
      return new Date(a.timestamp) - new Date(b.timestamp);
    }
    function byTimestampDesc(a, b) {
      return new Date(b.timestamp) - new Date(a.timestamp);
    }

    useEffect(() => {
      if (listRef.current) {
        listRef.current.scrollTop = listRef.current.scrollHeight;
      }
    }, [logs]);

    function clearLogs() {
      setLogs([]);
    }

    function submitTask(evn) {
      evn.preventDefault();
      if (taskInput.trim() && send) {
        send({ action: "submit_task", task: taskInput.trim() });
        setTaskInput("");
      }
    }

    return e(
      "div",
      { className: "container" },
      e(
        "div",
        { className: "header" },
        e("div", { className: "brand" }, "TaskAgent Logs UI"),
        e("div", { className: "controls" },
          e("div", { className: "status" }, `WS: ${status}`),
          e("button", { className: "btn", onClick: clearLogs }, "Clear")
        )
      ),
      // Task submission form
      e(
        "form",
        { onSubmit: submitTask, style: { display: "flex", gap: "8px", marginBottom: "12px" } },
        e("input", {
          type: "text",
          value: taskInput,
          onChange: (ev) => setTaskInput(ev.target.value),
          placeholder: "Enter a task...",
          style: { flex: 1, padding: "8px", borderRadius: "8px" },
        }),
        e("button", { className: "btn", type: "submit" }, "Submit Task")
      ),
      lastResponse
        ? e("div", { style: { marginBottom: "12px", color: "var(--info)" } }, lastResponse)
        : null,
      e(
        "div",
        { ref: listRef, className: "log-panel" },
        logs.length === 0
          ? e("div", { className: "empty" }, "No logs yet — connect your Python server.")
          : logs.map((log, idx) =>
              e(
                "div",
                { key: idx, className: "log-entry", title: log.message },
                e("div", { className: "log-meta" }, formatLocal(log.timestamp)),
                e(
                  "div",
                  { className: "message", style: { color: levelColor(log.level) } },
                  log.message
                )
              )
            )
      )
    );
  }

  const domRoot = document.getElementById("root");
  ReactDOM.createRoot(domRoot).render(React.createElement(App));
})();
