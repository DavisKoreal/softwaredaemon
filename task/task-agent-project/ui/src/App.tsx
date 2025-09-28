import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Search, Filter, Download, Trash2, RefreshCw, Send, Wifi, WifiOff, AlertCircle, CheckCircle, Info, AlertTriangle, Copy, ExternalLink } from 'lucide-react';

interface LogEntry {
  id: string;
  timestamp: string;
  message: string;
  type: 'info' | 'success' | 'error' | 'warning';
  duration?: number;
  metadata?: Record<string, any>;
}

interface TaskHistory {
  id: string;
  task: string;
  timestamp: string;
  status: 'pending' | 'completed' | 'failed';
}

const App: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filteredLogs, setFilteredLogs] = useState<LogEntry[]>([]);
  const [taskInput, setTaskInput] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [connectionAttempts, setConnectionAttempts] = useState(0);
  const [taskHistory, setTaskHistory] = useState<TaskHistory[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLogTypes, setSelectedLogTypes] = useState<Set<string>>(new Set(['info', 'success', 'error', 'warning']));
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [connectionHealth, setConnectionHealth] = useState<'healthy' | 'unstable' | 'failed'>('failed');
  const [lastActivity, setLastActivity] = useState<string>('');
  const [stats, setStats] = useState({ total: 0, success: 0, errors: 0, warnings: 0 });
  
  const logsEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [filteredLogs]);

  // Update stats when logs change
  useEffect(() => {
    const newStats = logs.reduce((acc, log) => {
      acc.total++;
      if (log.type === 'success') acc.success++;
      if (log.type === 'error') acc.errors++;
      if (log.type === 'warning') acc.warnings++;
      return acc;
    }, { total: 0, success: 0, errors: 0, warnings: 0 });
    setStats(newStats);
  }, [logs]);

  // Filter logs based on search and type filters
  useEffect(() => {
    let filtered = logs;
    
    if (searchTerm) {
      filtered = filtered.filter(log => 
        log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.timestamp.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    filtered = filtered.filter(log => selectedLogTypes.has(log.type));
    
    setFilteredLogs(filtered);
  }, [logs, searchTerm, selectedLogTypes]);

  const logToFile = useCallback(async (message: string, type: 'info' | 'success' | 'error' | 'warning' = 'info', metadata?: Record<string, any>) => {
    const logEntry: LogEntry = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      message,
      type,
      metadata
    };

    setLastActivity(new Date().toLocaleTimeString());

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
        id: `${Date.now() + 1}-${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date().toISOString(),
        message: `Failed to write log: ${error}`,
        type: 'error'
      };
      setLogs((prevLogs) => [...prevLogs, errorLog]);
    }
  }, []);

  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    logToFile('Establishing WebSocket connection...', 'info');
    const ws = new WebSocket('ws://localhost:8765');
    wsRef.current = ws;

    const connectionTimeout = setTimeout(() => {
      if (ws.readyState === WebSocket.CONNECTING) {
        ws.close();
        logToFile('Connection timeout - retrying...', 'warning');
      }
    }, 5000);

    ws.onopen = () => {
      clearTimeout(connectionTimeout);
      setIsConnected(true);
      setConnectionAttempts(0);
      setConnectionHealth('healthy');
      logToFile('WebSocket connected successfully', 'success', { endpoint: 'ws://localhost:8765' });
    };

    ws.onmessage = (event) => {
      let messageData;
      try {
        messageData = JSON.parse(event.data);
      } catch {
        messageData = { content: event.data };
      }
      
      logToFile(`Received: ${messageData.content || event.data}`, 'info', { 
        raw: event.data,
        parsed: messageData 
      });
      setLastActivity(new Date().toLocaleTimeString());
    };

    ws.onclose = (event) => {
      clearTimeout(connectionTimeout);
      setIsConnected(false);
      setConnectionHealth('failed');
      
      const reason = event.reason || 'Connection closed';
      logToFile(`WebSocket disconnected: ${reason}`, 'warning', { 
        code: event.code, 
        reason: event.reason,
        wasClean: event.wasClean 
      });
      
      // Smart reconnection strategy
      if (connectionAttempts < 10 && event.code !== 1000) {
        const delay = Math.min(Math.pow(2, connectionAttempts) * 1000, 30000);
        setConnectionAttempts(prev => prev + 1);
        setConnectionHealth('unstable');
        
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, delay);
        
        logToFile(`Auto-reconnecting in ${delay/1000}s (attempt ${connectionAttempts + 1}/10)`, 'info');
      }
    };

    ws.onerror = (error) => {
      clearTimeout(connectionTimeout);
      setIsConnected(false);
      setConnectionHealth('failed');
      logToFile('WebSocket connection failed', 'error', { error: error.toString() });
    };
  }, [connectionAttempts, logToFile]);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      wsRef.current?.close(1000, 'Component unmounting');
    };
  }, []);

  const handleTaskSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!taskInput.trim() || isSubmitting) return;

    const taskId = `task-${Date.now()}`;
    const trimmedTask = taskInput.trim();
    
    setIsSubmitting(true);
    await logToFile(`Submitting task: "${trimmedTask}"`, 'info', { taskId, length: trimmedTask.length });
    
    // Add to task history
    const newTask: TaskHistory = {
      id: taskId,
      task: trimmedTask,
      timestamp: new Date().toISOString(),
      status: 'pending'
    };
    setTaskHistory(prev => [newTask, ...prev.slice(0, 9)]); // Keep last 10 tasks
    
    try {
      const startTime = Date.now();
      const response = await fetch('/task.txt', {
        method: 'PUT',
        body: trimmedTask,
        headers: { 'Content-Type': 'text/plain' }
      });
      
      const duration = Date.now() - startTime;
      
      if (response.ok) {
        await logToFile(`Task submitted successfully`, 'success', { 
          taskId, 
          duration,
          response: { status: response.status, statusText: response.statusText }
        });
        setTaskInput('');
        
        // Update task history status
        setTaskHistory(prev => prev.map(task => 
          task.id === taskId ? { ...task, status: 'completed' as const } : task
        ));
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      await logToFile(`Task submission failed: ${errorMessage}`, 'error', { taskId, error: errorMessage });
      
      // Update task history status
      setTaskHistory(prev => prev.map(task => 
        task.id === taskId ? { ...task, status: 'failed' as const } : task
      ));
    } finally {
      setIsSubmitting(false);
    }
  };

  const clearLogs = () => {
    setLogs([]);
    setFilteredLogs([]);
    logToFile('All logs cleared by user', 'info');
  };

  const exportLogs = () => {
    const logData = logs.map(log => ({
      timestamp: log.timestamp,
      type: log.type,
      message: log.message,
      metadata: log.metadata
    }));
    
    const blob = new Blob([JSON.stringify(logData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `task-agent-logs-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    logToFile(`Exported ${logs.length} logs to file`, 'success');
  };

  const copyLogToClipboard = (log: LogEntry) => {
    const logText = `[${new Date(log.timestamp).toLocaleString()}] ${log.type.toUpperCase()}: ${log.message}`;
    navigator.clipboard.writeText(logText);
    logToFile('Log entry copied to clipboard', 'info');
  };

  const getLogIcon = (type: LogEntry['type']) => {
    switch (type) {
      case 'success': return CheckCircle;
      case 'error': return AlertCircle;
      case 'warning': return AlertTriangle;
      default: return Info;
    }
  };

  const getLogColorClass = (type: LogEntry['type']) => {
    switch (type) {
      case 'success': return 'text-green-700 bg-green-50 border-l-green-500 hover:bg-green-100';
      case 'error': return 'text-red-700 bg-red-50 border-l-red-500 hover:bg-red-100';
      case 'warning': return 'text-yellow-700 bg-yellow-50 border-l-yellow-500 hover:bg-yellow-100';
      default: return 'text-blue-700 bg-blue-50 border-l-blue-500 hover:bg-blue-100';
    }
  };

  const getConnectionStatusColor = () => {
    switch (connectionHealth) {
      case 'healthy': return 'bg-green-500';
      case 'unstable': return 'bg-yellow-500 animate-pulse';
      case 'failed': return 'bg-red-500';
      default: return 'bg-gray-400';
    }
  };

  const toggleLogTypeFilter = (type: string) => {
    const newSelected = new Set(selectedLogTypes);
    if (newSelected.has(type)) {
      newSelected.delete(type);
    } else {
      newSelected.add(type);
    }
    setSelectedLogTypes(newSelected);
  };

  const selectRecentTask = (task: string) => {
    setTaskInput(task);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="container mx-auto p-6 max-w-7xl">
        {/* Header with Stats */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 bg-clip-text text-transparent mb-3">
            Task Agent Control Center
          </h1>
          <p className="text-gray-600 text-lg mb-4">Advanced task management and monitoring dashboard</p>
          
          {/* Stats Bar */}
          <div className="flex justify-center space-x-6 text-sm">
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 rounded-full bg-blue-500"></div>
              <span className="text-gray-600">Total: {stats.total}</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-gray-600">Success: {stats.success}</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <span className="text-gray-600">Errors: {stats.errors}</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <span className="text-gray-600">Warnings: {stats.warnings}</span>
            </div>
          </div>
        </div>

        {/* Enhanced Status Card */}
        <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className={`w-4 h-4 rounded-full ${getConnectionStatusColor()}`}></div>
              <span className="text-lg font-semibold flex items-center space-x-2">
                {isConnected ? <Wifi className="w-5 h-5 text-green-600" /> : <WifiOff className="w-5 h-5 text-red-600" />}
                <span>WebSocket: {connectionHealth.charAt(0).toUpperCase() + connectionHealth.slice(1)}</span>
              </span>
            </div>
            <div className="flex items-center space-x-3">
              {lastActivity && (
                <span className="text-sm text-gray-600">Last activity: {lastActivity}</span>
              )}
              <button
                onClick={connectWebSocket}
                disabled={isConnected}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-2"
              >
                <RefreshCw className={`w-4 h-4 ${isSubmitting ? 'animate-spin' : ''}`} />
                <span>Reconnect</span>
              </button>
            </div>
          </div>
          {connectionAttempts > 0 && !isConnected && (
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 rounded">
              <div className="flex items-center">
                <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2" />
                <span className="text-sm text-yellow-700">
                  Reconnecting... Attempt {connectionAttempts}/10
                </span>
              </div>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
          {/* Enhanced Task Input Section */}
          <div className="xl:col-span-1">
            <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6 mb-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center text-gray-800">
                <Send className="mr-2 w-5 h-5" />
                Submit New Task
              </h2>
              <div className="space-y-4">
                <div>
                  <textarea
                    value={taskInput}
                    onChange={(e) => setTaskInput(e.target.value)}
                    placeholder="Describe your task in detail..."
                    className="w-full h-32 p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none transition-all duration-200 bg-white/50"
                    disabled={isSubmitting}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                        handleTaskSubmit();
                      }
                    }}
                  />
                  <div className="text-xs text-gray-500 mt-1">
                    {taskInput.length} characters • Press Ctrl+Enter to submit
                  </div>
                </div>
                <button
                  onClick={handleTaskSubmit}
                  disabled={!isConnected || !taskInput.trim() || isSubmitting}
                  className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 px-6 rounded-xl font-semibold
                    hover:from-indigo-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 
                    disabled:cursor-not-allowed transform transition-all duration-200 hover:scale-[1.02] disabled:scale-100
                    flex items-center justify-center space-x-2 shadow-lg"
                >
                  {isSubmitting ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Submitting...</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      <span>Submit Task</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Task History */}
            {taskHistory.length > 0 && (
              <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6">
                <h3 className="text-lg font-semibold mb-3 text-gray-800">Recent Tasks</h3>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {taskHistory.map((task) => (
                    <div 
                      key={task.id} 
                      className="p-3 rounded-lg bg-gray-50 hover:bg-gray-100 cursor-pointer transition-colors duration-200 border border-gray-200"
                      onClick={() => selectRecentTask(task.task)}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          task.status === 'completed' ? 'bg-green-100 text-green-800' :
                          task.status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {task.status}
                        </span>
                        <span className="text-xs text-gray-500">
                          {new Date(task.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 truncate">{task.task}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Enhanced Logs Section */}
          <div className="xl:col-span-3">
            <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6 h-[700px] flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold flex items-center text-gray-800">
                  <Info className="mr-2 w-5 h-5" />
                  Activity Logs
                  <span className="ml-2 text-sm bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full">
                    {filteredLogs.length}/{logs.length}
                  </span>
                </h2>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setIsFilterOpen(!isFilterOpen)}
                    className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors duration-200 flex items-center space-x-1"
                  >
                    <Filter className="w-4 h-4" />
                    <span>Filter</span>
                  </button>
                  <button
                    onClick={exportLogs}
                    className="px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors duration-200 flex items-center space-x-1"
                  >
                    <Download className="w-4 h-4" />
                    <span>Export</span>
                  </button>
                  <button
                    onClick={clearLogs}
                    className="px-3 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors duration-200 flex items-center space-x-1"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>Clear</span>
                  </button>
                </div>
              </div>

              {/* Search and Filter Controls */}
              <div className="space-y-3 mb-4">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search logs..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white/50"
                  />
                </div>

                {isFilterOpen && (
                  <div className="flex flex-wrap gap-2 p-3 bg-gray-50 rounded-lg">
                    {['info', 'success', 'error', 'warning'].map((type) => (
                      <button
                        key={type}
                        onClick={() => toggleLogTypeFilter(type)}
                        className={`px-3 py-1 rounded-full text-sm transition-colors duration-200 ${
                          selectedLogTypes.has(type)
                            ? type === 'info' ? 'bg-blue-100 text-blue-800' :
                              type === 'success' ? 'bg-green-100 text-green-800' :
                              type === 'error' ? 'bg-red-100 text-red-800' :
                              'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                        }`}
                      >
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              
              <div className="flex-1 overflow-hidden rounded-xl border border-gray-200">
                <div className="h-full overflow-y-auto bg-gray-50/50 p-4 space-y-2">
                  {filteredLogs.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-gray-500">
                      <div className="text-center">
                        <Info className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                        <p className="text-lg mb-2">No logs match your criteria</p>
                        <p className="text-sm">
                          {logs.length === 0 ? 'Submit a task to get started!' : 'Try adjusting your search or filters.'}
                        </p>
                      </div>
                    </div>
                  ) : (
                    filteredLogs.map((log) => {
                      const IconComponent = getLogIcon(log.type);
                      return (
                        <div
                          key={log.id}
                          className={`p-3 rounded-lg border-l-4 ${getLogColorClass(log.type)} 
                            transform transition-all duration-200 hover:scale-[1.005] hover:shadow-sm group cursor-pointer`}
                          onClick={() => copyLogToClipboard(log)}
                        >
                          <div className="flex items-start space-x-3">
                            <IconComponent className="w-5 h-5 mt-0.5 flex-shrink-0" />
                            <div className="flex-1 min-w-0">
                              <div className="flex items-start justify-between">
                                <p className="text-sm font-medium break-words leading-relaxed">{log.message}</p>
                                <div className="flex items-center space-x-2 ml-3 flex-shrink-0">
                                  <span className="text-xs opacity-75 whitespace-nowrap">
                                    {new Date(log.timestamp).toLocaleTimeString()}
                                  </span>
                                  <Copy className="w-3 h-3 opacity-0 group-hover:opacity-50 transition-opacity" />
                                </div>
                              </div>
                              {log.metadata && (
                                <div className="mt-2 text-xs opacity-75">
                                  <details className="cursor-pointer">
                                    <summary className="hover:opacity-100">View metadata</summary>
                                    <pre className="mt-1 text-xs bg-black/10 p-2 rounded overflow-x-auto">
                                      {JSON.stringify(log.metadata, null, 2)}
                                    </pre>
                                  </details>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })
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