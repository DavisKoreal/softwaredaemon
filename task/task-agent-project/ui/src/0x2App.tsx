import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronRight, Clock, AlertTriangle, CheckCircle, Code, FileText, Server, Play, Square } from 'lucide-react';

interface LogEntryProps {
  timestamp: string;
  level: 'info' | 'error' | 'success' | 'warning';
  message: string;
  children?: React.ReactNode;
  icon?: React.ComponentType<{ size?: number; className?: string }>;
}

// 1. LogEntry Component - Base component for individual log entries
const LogEntry: React.FC<LogEntryProps> = ({ timestamp, level, message, children, icon: Icon = Clock }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const levelColors = {
    info: 'text-blue-600 bg-blue-50',
    error: 'text-red-600 bg-red-50',
    success: 'text-green-600 bg-green-50',
    warning: 'text-yellow-600 bg-yellow-50'
  };

  return (
    <div className={`border rounded-lg mb-2 ${levelColors[level] || 'text-gray-600 bg-gray-50'}`}>
      <div
        className="p-3 flex items-center gap-3 cursor-pointer hover:bg-opacity-80"
        onClick={() => children && setIsExpanded(!isExpanded)}
      >
        <Icon size={16} />
        <span className="text-sm font-mono text-gray-500 min-w-0 flex-shrink-0">
          {timestamp}
        </span>
        <span className="flex-1 text-sm">{message}</span>
        {children && (
          isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />
        )}
      </div>
      {children && isExpanded && (
        <div className="px-6 pb-3 border-t border-current border-opacity-20">
          {children}
        </div>
      )}
    </div>
  );
};

interface Task {
  name: string;
  timestamp: string;
  status: 'completed' | 'error' | 'running' | 'pending';
  subtasks: string[];
}

interface TaskTimelineProps {
  tasks: Task[];
}

// 2. TaskTimeline Component - Shows task progression and lifecycle
const TaskTimeline: React.FC<TaskTimelineProps> = ({ tasks }) => {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Task Timeline</h3>
      {tasks.map((task, index) => (
        <div key={index} className="relative">
          {/* Timeline line */}
          {index < tasks.length - 1 && (
            <div className="absolute left-4 top-8 w-0.5 h-8 bg-gray-300"></div>
          )}

          <div className="flex items-start gap-3">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold
              ${task.status === 'completed' ? 'bg-green-500' :
                task.status === 'error' ? 'bg-red-500' :
                task.status === 'running' ? 'bg-blue-500' : 'bg-gray-400'}`}>
              {task.status === 'completed' ? <CheckCircle size={16} /> :
               task.status === 'error' ? <AlertTriangle size={16} /> :
               task.status === 'running' ? <Play size={16} /> : <Square size={16} />}
            </div>

            <div className="flex-1">
              <div className="bg-white border rounded-lg p-3 shadow-sm">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium text-gray-800">{task.name}</h4>
                  <span className="text-xs text-gray-500">{task.timestamp}</span>
                </div>

                {task.subtasks && task.subtasks.length > 0 && (
                  <div className="mt-2">
                    <div className="text-sm text-gray-600 mb-1">
                      Subtasks ({task.subtasks.length}):
                    </div>
                    <ul className="space-y-1">
                      {task.subtasks.map((subtask, idx) => (
                        <li key={idx} className="text-xs text-gray-500 pl-4 border-l-2 border-gray-200">
                          {subtask}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

interface APIResponseViewerProps {
  response: string;
  timestamp: string;
  isError?: boolean;
}

// 3. APIResponseViewer Component - Displays formatted API responses with JSON syntax highlighting
const APIResponseViewer: React.FC<APIResponseViewerProps> = ({ response, timestamp, isError = false }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Simple JSON formatter for display
  const formatJSON = (jsonString: string) => {
    try {
      const parsed = JSON.parse(jsonString);
      return JSON.stringify(parsed, null, 2);
    } catch {
      return jsonString;
    }
  };

  return (
    <div className={`border rounded-lg ${isError ? 'border-red-300 bg-red-50' : 'border-blue-300 bg-blue-50'}`}>
      <div
        className="p-3 flex items-center gap-3 cursor-pointer hover:bg-opacity-80"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <Code size={16} className={isError ? 'text-red-600' : 'text-blue-600'} />
        <span className="text-sm font-mono text-gray-500">{timestamp}</span>
        <span className={`text-sm font-medium ${isError ? 'text-red-700' : 'text-blue-700'}`}>
          {isError ? 'API Error' : 'API Response'}
        </span>
        {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
      </div>

      {isExpanded && (
        <div className="px-3 pb-3">
          <pre className="bg-gray-800 text-green-400 p-3 rounded text-xs overflow-x-auto font-mono">
            {formatJSON(response)}
          </pre>
        </div>
      )}
    </div>
  );
};

interface SystemStatusIndicatorProps {
  status: 'starting' | 'running' | 'shutting_down' | 'stopped' | 'error';
  timestamp: string;
  details?: string;
}

// 4. SystemStatusIndicator Component - Shows server/system status changes
const SystemStatusIndicator: React.FC<SystemStatusIndicatorProps> = ({ status, timestamp, details }) => {
  const statusConfig = {
    starting: { color: 'bg-yellow-500', icon: Play, label: 'Starting' },
    running: { color: 'bg-green-500', icon: CheckCircle, label: 'Running' },
    shutting_down: { color: 'bg-orange-500', icon: Square, label: 'Shutting Down' },
    stopped: { color: 'bg-red-500', icon: AlertTriangle, label: 'Stopped' },
    error: { color: 'bg-red-600', icon: AlertTriangle, label: 'Error' }
  };

  const config = statusConfig[status] || statusConfig.stopped;
  const Icon = config.icon;

  return (
    <div className="flex items-center gap-3 p-3 bg-white border rounded-lg shadow-sm">
      <div className={`w-3 h-3 rounded-full ${config.color} animate-pulse`}></div>
      <Icon size={16} className="text-gray-600" />
      <div className="flex-1">
        <div className="flex justify-between items-center">
          <span className="font-medium text-gray-800">{config.label}</span>
          <span className="text-sm text-gray-500 font-mono">{timestamp}</span>
        </div>
        {details && <div className="text-sm text-gray-600 mt-1">{details}</div>}
      </div>
    </div>
  );
};

interface CodeGenerationPreviewProps {
  filename: string;
  code: string;
  language?: string;
  timestamp: string;
}

// 5. CodeGenerationPreview Component - Shows generated code snippets
const CodeGenerationPreview: React.FC<CodeGenerationPreviewProps> = ({ filename, code, language = 'cpp', timestamp }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="border border-purple-300 bg-purple-50 rounded-lg">
      <div
        className="p-3 flex items-center gap-3 cursor-pointer hover:bg-purple-100"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <FileText size={16} className="text-purple-600" />
        <span className="font-medium text-purple-800">{filename}</span>
        <span className="text-sm text-purple-600">({language})</span>
        <span className="text-sm font-mono text-gray-500 ml-auto">{timestamp}</span>
        {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
      </div>

      {isExpanded && (
        <div className="px-3 pb-3">
          <pre className="bg-gray-900 text-gray-100 p-3 rounded text-sm overflow-x-auto">
            <code>{code}</code>
          </pre>
        </div>
      )}
    </div>
  );
};

interface ErrorAlertProps {
  error: string;
  timestamp: string;
  severity?: 'error' | 'warning';
}

// 6. ErrorAlert Component - Highlights errors and warnings
const ErrorAlert: React.FC<ErrorAlertProps> = ({ error, timestamp, severity = 'error' }) => {
  const severityConfig = {
    error: { bg: 'bg-red-100', border: 'border-red-400', text: 'text-red-800', icon: AlertTriangle },
    warning: { bg: 'bg-yellow-100', border: 'border-yellow-400', text: 'text-yellow-800', icon: AlertTriangle }
  };

  const config = severityConfig[severity];
  const Icon = config.icon;

  return (
    <div className={`${config.bg} ${config.border} border-l-4 p-4 rounded-r-lg`}>
      <div className="flex items-start gap-3">
        <Icon size={20} className={config.text} />
        <div className="flex-1">
          <div className="flex justify-between items-start">
            <h4 className={`font-medium ${config.text} mb-1`}>
              {severity === 'error' ? 'Error' : 'Warning'}
            </h4>
            <span className="text-sm text-gray-500 font-mono">{timestamp}</span>
          </div>
          <p className={`text-sm ${config.text}`}>{error}</p>
        </div>
      </div>
    </div>
  );
};

interface Filters {
  startDate: string;
  endDate: string;
  level: string;
  search: string;
}

interface LogFilterControlsProps {
  filters: Filters;
  onFilterChange: (key: keyof Filters, value: string) => void;
}

// 7. LogFilterControls Component - Provides filtering options for logs
const LogFilterControls: React.FC<LogFilterControlsProps> = ({ filters, onFilterChange }) => {
  return (
    <div className="bg-white p-4 border rounded-lg shadow-sm mb-4">
      <h3 className="text-sm font-medium text-gray-700 mb-3">Filter Logs</h3>
      <div className="flex flex-wrap gap-4">
        {/* Date Range */}
        <div className="flex gap-2">
          <input
            type="datetime-local"
            className="text-xs border rounded px-2 py-1"
            value={filters.startDate}
            onChange={(e) => onFilterChange('startDate', e.target.value)}
          />
          <span className="text-gray-500 self-center">to</span>
          <input
            type="datetime-local"
            className="text-xs border rounded px-2 py-1"
            value={filters.endDate}
            onChange={(e) => onFilterChange('endDate', e.target.value)}
          />
        </div>

        {/* Log Level */}
        <select
          className="text-xs border rounded px-2 py-1"
          value={filters.level}
          onChange={(e) => onFilterChange('level', e.target.value)}
        >
          <option value="">All Levels</option>
          <option value="info">Info</option>
          <option value="warning">Warning</option>
          <option value="error">Error</option>
          <option value="success">Success</option>
        </select>

        {/* Search */}
        <input
          type="text"
          placeholder="Search logs..."
          className="text-xs border rounded px-2 py-1 flex-1 min-w-48"
          value={filters.search}
          onChange={(e) => onFilterChange('search', e.target.value)}
        />
      </div>
    </div>
  );
};

interface ApiResponse {
  response: string;
  timestamp: string;
}

interface CodePreview {
  filename: string;
  code: string;
  language: string;
  timestamp: string;
}

interface ErrorItem {
  error: string;
  timestamp: string;
  severity: 'error' | 'warning';
}

interface Status {
  status: 'starting' | 'running' | 'shutting_down' | 'stopped' | 'error';
  timestamp: string;
  details: string;
}

interface LogData {
  timestamp: string;
  message: string;
  level: string;
}

interface GeneralLog extends LogData {}

// Main App Component - Upgraded with general logs section, improved filtering including dates and levels
const App: React.FC = () => {
  const [filters, setFilters] = useState<Filters>({
    startDate: '',
    endDate: '',
    level: '',
    search: ''
  });

  const [tasks, setTasks] = useState<Task[]>([]);
  const [apiResponses, setApiResponses] = useState<ApiResponse[]>([]);
  const [codePreviews, setCodePreviews] = useState<CodePreview[]>([]);
  const [errors, setErrors] = useState<ErrorItem[]>([]);
  const [statuses, setStatuses] = useState<Status[]>([]);
  const [generalLogs, setGeneralLogs] = useState<GeneralLog[]>([]);
  const [newTask, setNewTask] = useState('');

  const handleFilterChange = (key: keyof Filters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleSubmitTask = () => {
    fetch('http://localhost:8000/task.txt', {
      method: 'PUT',
      body: newTask,
      headers: { 'Content-Type': 'text/plain' }
    })
    .then(() => {
      setNewTask('');
      // Optionally show success
    })
    .catch(err => console.error(err));
  };

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8765');

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data: LogData = JSON.parse(event.data);
      processLogData(data);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return () => ws.close();
  }, []);

  const processLogData = (data: LogData) => {
    // Always add to general logs
    setGeneralLogs(prev => [...prev, data]);

    const { timestamp, message, level } = data;

    if (level === 'task_process' || message.startsWith('Processing new task:')) {
      const name = message.replace('Processing new task: ', '');
      setTasks(prev => [...prev, { name, timestamp, status: 'running', subtasks: [] }]);
    }

    if (level === 'api_response' || message.startsWith('Response from the API:')) {
      const response = message.replace('Response from the API: ', '');
      setApiResponses(prev => [...prev, { response, timestamp }]);

      try {
        const respJson = JSON.parse(response);
        if (respJson.atomic === 'false') {
          setTasks(prev => {
            if (prev.length === 0) return prev;
            const newTasks = [...prev];
            newTasks[newTasks.length - 1].subtasks = respJson.subtasks;
            return newTasks;
          });
        } else if (respJson.atomic === 'true') {
          const cmd = respJson.command;
          // Extract from python -c "with open('filename', 'w'...) as f: f.write('''code''')"
          const match = cmd.match(/open\(['"]([^'"]+)['"], 'w'[^)]*\) as f: f\.write\(\'''([\s\S]*?)'''\)/);
          if (match) {
            const filename = match[1];
            const code = match[2];
            const language = filename.split('.').pop();
            setCodePreviews(prev => [...prev, { filename, code, language, timestamp }]);
          }
        }
      } catch (e) {
        console.error('Failed to parse API response:', e);
      }
    }

    if (level === 'error' || message.includes('error')) {
      setErrors(prev => [...prev, { error: message, timestamp, severity: 'error' }]);
      // If related to task, update task status to error
      if (tasks.length > 0) {
        setTasks(prev => {
          const newTasks = [...prev];
          newTasks[newTasks.length - 1].status = 'error';
          return newTasks;
        });
      }
    }

    if (level === 'system_start' || message === 'Starting task.txt file monitoring') {
      setStatuses(prev => [...prev, { status: 'starting', timestamp, details: message }]);
    } else if (level === 'system_shutdown' || message === 'Shutting down server') {
      setStatuses(prev => [...prev, { status: 'shutting_down', timestamp, details: message }]);
    } else if (message.includes('HTTP server error')) {
      setStatuses(prev => [...prev, { status: 'error', timestamp, details: message }]);
    } else if (level === 'command_result' && message.includes('The result of the command')) {
      // Optionally update task to completed if no error
      if (!message.includes('Error') && tasks.length > 0) {
        setTasks(prev => {
          const newTasks = [...prev];
          newTasks[newTasks.length - 1].status = 'completed';
          return newTasks;
        });
      }
    }
  };

  // Filter functions with date and level support
  const filterItems = <T extends { timestamp: string }>(items: T[], checkLevel?: (item: T) => string) => {
    return items.filter(item => {
      const itemDate = new Date(item.timestamp);
      if (filters.startDate && itemDate < new Date(filters.startDate)) return false;
      if (filters.endDate && itemDate > new Date(filters.endDate)) return false;
      if (filters.level && checkLevel && checkLevel(item) !== filters.level) return false;
      if (filters.search && !JSON.stringify(item).toLowerCase().includes(filters.search.toLowerCase())) return false;
      return true;
    });
  };

  const filteredTasks = filterItems(tasks);
  const filteredApiResponses = filterItems(apiResponses);
  const filteredCodePreviews = filterItems(codePreviews);
  const filteredErrors = filterItems(errors, item => item.severity);
  const filteredStatuses = filterItems(statuses, item => item.status === 'error' ? 'error' : 'info');
  const filteredGeneralLogs = filterItems(generalLogs, item => item.level);

  return (
    <div className="max-w-6xl mx-auto p-6 bg-gray-50 min-h-screen">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Task Agent Dashboard (Upgraded)</h1>

      {/* Task Submission */}
      <div className="bg-white p-4 border rounded-lg shadow-sm mb-4">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Submit New Task</h3>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Enter task (e.g., simulate a transistor using c++)"
            className="flex-1 border rounded px-3 py-2"
            value={newTask}
            onChange={(e) => setNewTask(e.target.value)}
          />
          <button
            onClick={handleSubmitTask}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Submit
          </button>
        </div>
      </div>

      {/* Filter Controls */}
      <LogFilterControls filters={filters} onFilterChange={handleFilterChange} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          {/* Task Timeline */}
          <div className="bg-white p-4 rounded-lg shadow">
            <TaskTimeline tasks={filteredTasks} />
          </div>

          {/* System Status */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-800">System Status</h3>
            {filteredStatuses.map((status, idx) => (
              <SystemStatusIndicator key={idx} {...status} />
            ))}
          </div>

          {/* General Logs - New section for all logs */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-800">All Logs</h3>
            <div className="max-h-96 overflow-y-auto border rounded-lg p-2 bg-white">
              {filteredGeneralLogs.map((log, idx) => (
                <LogEntry key={idx} timestamp={log.timestamp} level={log.level as any} message={log.message} />
              ))}
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* API Responses */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-800">API Responses</h3>
            {filteredApiResponses.map((resp, idx) => (
              <APIResponseViewer key={idx} {...resp} />
            ))}
          </div>

          {/* Code Generation */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-800">Generated Code</h3>
            {filteredCodePreviews.map((preview, idx) => (
              <CodeGenerationPreview key={idx} {...preview} />
            ))}
          </div>

          {/* Errors */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-800">Errors & Warnings</h3>
            {filteredErrors.map((err, idx) => (
              <ErrorAlert key={idx} {...err} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;