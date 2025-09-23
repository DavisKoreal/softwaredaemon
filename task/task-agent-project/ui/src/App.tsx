import React, { useState, useEffect, useRef } from 'react';
import './App.css';

interface LogEntry {
  id: string;
  timestamp: string;
  message: string;
  type: 'info' | 'success' | 'error' | 'warning';
}

const App: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [taskInput, setTaskInput] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [connectionAttempts, setConnectionAttempts] = useState(0);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  // Enhanced logging with types
  const logToFile = async (message: string, type: 'info' | 'success' | 'error' | 'warning' = 'info') => {
    const logEntry: LogEntry = {
      id: Date.now().toString(),
      timestamp: new Date().toLocaleString(),
      message,
      type
    };

    try {
      await fetch('/log-ui', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logEntry),
      });
      setLogs((prevLogs) => [...prevLogs, logEntry]);
    } catch (error) {
      console.error('Error logging to file:', error);
      const errorLog: LogEntry = {
        id: (Date.now() + 1).toString(),
        timestamp: new Date().toLocaleString(),
        message: `Error logging to file: ${error}`,
        type: 'error'
      };
      setLogs((prevLogs) => [...prevLogs, errorLog]);
    }
  };

  const connectWebSocket = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    
    logToFile('Initializing WebSocket connection', 'info');
    const ws = new WebSocket('ws://localhost:8765');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      setConnectionAttempts(0);
      logToFile('WebSocket connection established', 'success');
    };

    ws.onmessage = (event) => {
      const message = `Received: ${event.data}`;
      logToFile(message, 'info');
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      logToFile('WebSocket connection closed', 'warning');
      
      // Auto-reconnect with exponential backoff
      if (connectionAttempts < 5) {
        const delay = Math.pow(2, connectionAttempts) * 1000;
        setTimeout(() => {
          setConnectionAttempts(prev => prev + 1);
          connectWebSocket();
        }, delay);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
      logToFile(`WebSocket error: ${error}`, 'error');
    };
  };

  useEffect(() => {
    connectWebSocket();
    return () => {
      wsRef.current?.close();
      logToFile('WebSocket connection cleanup', 'info');
    };
  }, []);

  const handleTaskSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!taskInput.trim() || isSubmitting) return;

    setIsSubmitting(true);
    await logToFile(`Submitting task: ${taskInput}`, 'info');
    
    try {
      const response = await fetch('/task.txt', {
        method: 'PUT',
        body: taskInput,
        headers: { 'Content-Type': 'text/plain' }
      });
      
      if (response.ok) {
        await logToFile(`Task submitted successfully: ${taskInput}`, 'success');
        setTaskInput('');
      } else {
        throw new Error(`Server responded with status: ${response.status}`);
      }
    } catch (error) {
      console.error('Error submitting task:', error);
      await logToFile(`Error submitting task: ${error}`, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const clearLogs = () => {
    setLogs([]);
    logToFile('Logs cleared by user', 'info');
  };

  const getLogIcon = (type: LogEntry['type']) => {
    switch (type) {
      case 'success': return 'âœ…';
      case 'error': return 'âŒ';
      case 'warning': return 'âš ï¸';
      default: return 'â„¹ï¸';
    }
  };

  const getLogColorClass = (type: LogEntry['type']) => {
    switch (type) {
      case 'success': return 'text-green-700 bg-green-50 border-l-green-500';
      case 'error': return 'text-red-700 bg-red-50 border-l-red-500';
      case 'warning': return 'text-yellow-700 bg-yellow-50 border-l-yellow-500';
      default: return 'text-blue-700 bg-blue-50 border-l-blue-500';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <div className="container mx-auto p-6 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-2">
            Task Agent Control Center
          </h1>
          <p className="text-gray-600">Manage and monitor your automated tasks</p>
        </div>

        {/* Status Card */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`w-4 h-4 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
              <span className="text-lg font-semibold">
                WebSocket Status: {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            {!isConnected && (
              <button
                onClick={connectWebSocket}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200"
              >
                Reconnect
              </button>
            )}
          </div>
          {connectionAttempts > 0 && !isConnected && (
            <div className="mt-2 text-sm text-gray-600">
              Connection attempt: {connectionAttempts}/5
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Task Input Section */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <span className="mr-2">ðŸŽ¯</span>
                Submit New Task
              </h2>
              <form onSubmit={handleTaskSubmit} className="space-y-4">
                <div>
                  <textarea
                    value={taskInput}
                    onChange={(e) => setTaskInput(e.target.value)}
                    placeholder="Enter your task description..."
                    className="w-full h-32 p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none transition-all duration-200"
                    disabled={isSubmitting}
                  />
                </div>
                <button
                  type="submit"
                  disabled={!isConnected || !taskInput.trim() || isSubmitting}
                  className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 px-6 rounded-xl font-semibold
                    hover:from-indigo-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 
                    disabled:cursor-not-allowed transform transition-all duration-200 hover:scale-[1.02] disabled:scale-100
                    flex items-center justify-center space-x-2"
                >
                  {isSubmitting ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Submitting...</span>
                    </>
                  ) : (
                    <>
                      <span>ðŸš€</span>
                      <span>Submit Task</span>
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Logs Section */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 h-[600px] flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold flex items-center">
                  <span className="mr-2">ðŸ“‹</span>
                  Activity Logs
                  <span className="ml-2 text-sm bg-indigo-100 text-indigo-800 px-2 py-1 rounded-full">
                    {logs.length}
                  </span>
                </h2>
                <button
                  onClick={clearLogs}
                  className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors duration-200 text-sm font-medium"
                >
                  Clear Logs
                </button>
              </div>
              
              <div className="flex-1 overflow-hidden rounded-xl border border-gray-200">
                <div className="h-full overflow-y-auto bg-gray-50 p-4 space-y-2">
                  {logs.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-gray-500">
                      <div className="text-center">
                        <div className="text-6xl mb-4">ðŸ“</div>
                        <p>No logs yet. Submit a task to get started!</p>
                      </div>
                    </div>
                  ) : (
                    logs.map((log) => (
                      <div
                        key={log.id}
                        className={`p-3 rounded-lg border-l-4 ${getLogColorClass(log.type)} 
                          transform transition-all duration-200 hover:scale-[1.01] hover:shadow-sm`}
                      >
                        <div className="flex items-start space-x-2">
                          <span className="text-lg">{getLogIcon(log.type)}</span>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <p className="text-sm font-medium break-words">{log.message}</p>
                              <span className="text-xs opacity-75 whitespace-nowrap ml-2">
                                {new Date(log.timestamp).toLocaleTimeString()}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                  <div ref={logsEndRef} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
