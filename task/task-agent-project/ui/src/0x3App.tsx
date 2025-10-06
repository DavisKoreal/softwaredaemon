import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronRight, AlertTriangle, CheckCircle, Play, Send } from 'lucide-react';

interface Log {
  id: number;
  timestamp: string;
  message: string;
  level: 'info' | 'error' | 'warning' | 'success';
}

const App: React.FC = () => {
  const [logs, setLogs] = useState<Log[]>([]);
  const [task, setTask] = useState('');
  const [filter, setFilter] = useState('');
  const [expandedLogs, setExpandedLogs] = useState(new Set<number>());

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8766');
    
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      setLogs(prev => [...prev, { ...data, id: Date.now() + Math.random() }]);
    };

    return () => ws.close();
  }, []);

  const submitTask = () => {
    fetch('http://localhost:8000/task.txt', {
      method: 'PUT',
      body: task,
      headers: { 'Content-Type': 'text/plain' }
    }).then(() => setTask(''));
  };

  const toggleExpand = (id: number) => {
    setExpandedLogs(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const getLevelStyle = (level: string): string => ({
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    success: 'bg-green-50 border-green-200 text-green-800'
  }[level] || 'bg-gray-50 border-gray-200 text-gray-800');

  const getIcon = (level: string) => {
    if (level === 'error') return <AlertTriangle size={16} />;
    if (level === 'success') return <CheckCircle size={16} />;
    return <Play size={16} />;
  };

  const filtered = logs.filter(log => 
    !filter || log.message.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">Task Agent</h1>
        
        {/* Task Input */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={task}
              onChange={(e) => setTask(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && submitTask()}
              placeholder="Enter task (e.g., simulate a transistor using c++)"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={submitTask}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Send size={16} /> Submit
            </button>
          </div>
        </div>

        {/* Filter */}
        <div className="bg-white rounded-lg shadow p-4">
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filter logs..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Logs */}
        <div className="bg-white rounded-lg shadow p-4 space-y-2 max-h-[600px] overflow-y-auto">
          <h2 className="text-lg font-semibold mb-3">Activity Log ({filtered.length})</h2>
          {filtered.map(log => {
            const expanded = expandedLogs.has(log.id);
            const hasDetails = log.message.length > 100;
            
            return (
              <div
                key={log.id}
                className={`border rounded-lg p-3 ${getLevelStyle(log.level)}`}
              >
                <div
                  className="flex items-start gap-3 cursor-pointer"
                  onClick={() => hasDetails && toggleExpand(log.id)}
                >
                  {getIcon(log.level)}
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-start gap-2">
                      <span className="text-sm font-medium break-words">
                        {expanded || !hasDetails 
                          ? log.message 
                          : log.message.slice(0, 100) + '...'}
                      </span>
                      <span className="text-xs text-gray-500 whitespace-nowrap">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                  {hasDetails && (
                    expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default App;