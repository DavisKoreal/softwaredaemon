import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronRight, AlertTriangle, CheckCircle, Play, Send } from 'lucide-react';
import { useWebSocket, ReceivedData } from './useWebSocket'; // Assuming useWebSocket.ts is in the same directory

interface Log {
    id: number;
    timestamp: string;
    message: string;
    level: 'info' | 'error' | 'warning' | 'success';
}

const WS_URL = 'ws://localhost:8766';

const App: React.FC = () => {
    const { isConnected, latestMessage, sendMessage } = useWebSocket(WS_URL);

    const [logs, setLogs] = useState<Log[]>([]);
    const [task, setTask] = useState('');
    const [filter, setFilter] = useState('');
    const [expandedLogs, setExpandedLogs] = useState(new Set<number>());

    // Effect to process incoming messages from the hook
    useEffect(() => {
        if (!latestMessage) return;

        const timestamp = new Date().toISOString();
        const id = Date.now() + Math.random();

        if (latestMessage.level) {
            // Process incoming backend log messages (info, error, etc.)
            const newLog: Log = {
                id,
                timestamp: latestMessage.timestamp || timestamp,
                message: latestMessage.message || 'Unknown log message',
                level: latestMessage.level || 'info',
            };
            setLogs(prev => [...prev, newLog]);
        } else if (latestMessage.response === 'task_submitted') {
            // Handle successful task submission confirmation
            setLogs(prev => [...prev, { 
                id, 
                timestamp, 
                message: `Task submitted successfully: ${latestMessage.task}`, 
                level: 'success' 
            }]);
        } else if (latestMessage.error) {
            // Handle errors sent from the backend
            setLogs(prev => [...prev, { 
                id, 
                timestamp, 
                message: `Backend Error: ${latestMessage.error}`, 
                level: 'error' 
            }]);
        } else {
            // Handle unhandled responses for debugging
            console.log('Received unhandled data:', latestMessage);
        }
    }, [latestMessage]);

    // Handle the initial connection status for logging
    useEffect(() => {
        if (isConnected) {
            setLogs(prev => [...prev, { 
                id: Date.now() + Math.random(), 
                timestamp: new Date().toISOString(), 
                message: `Client connected to WebSocket server at ${WS_URL}`, 
                level: 'info' 
            }]);
        } else {
             // Avoid logging failure on first Strict Mode cleanup
             if (logs.length > 0) { 
                setLogs(prev => [...prev, { 
                    id: Date.now() + Math.random(), 
                    timestamp: new Date().toISOString(), 
                    message: 'WebSocket disconnected.', 
                    level: 'warning' 
                }]);
             }
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isConnected]);
    

    const submitTask = () => {
        const taskText = task.trim();
        if (!taskText) return;

        const message = {
            action: 'submit_task',
            task: taskText,
        };
        
        // Use the hook's sender function
        const sent = sendMessage(message);

        if (sent) {
            setTask(''); // Clear input only if sent
        } else {
            setLogs(prev => [...prev, { 
                id: Date.now() + Math.random(), 
                timestamp: new Date().toISOString(), 
                message: 'Connection error: WebSocket is not open. Cannot submit task.', 
                level: 'error' 
            }]);
        }
    };

    const toggleExpand = (id: number) => {
        setExpandedLogs(prev => {
            const next = new Set(prev);
            next.has(id) ? next.delete(id) : next.add(id);
            return next;
        });
    };

    // --- Presentation Logic (Unchanged) ---
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
    // ------------------------------------

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-5xl mx-auto space-y-4">
                <h1 className="text-3xl font-bold text-gray-900">Task Agent</h1>
                <p className={`text-sm font-medium ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
                    Connection Status: {isConnected ? 'Connected' : 'Disconnected'}
                </p>

                {/* Task Input */}
                <div className="bg-white rounded-lg shadow p-4">
                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={task}
                            id="task-input"
                            name="task-input"
                            onChange={(e) => setTask(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && submitTask()}
                            placeholder="Enter task (e.g., simulate a transistor using c++)"
                            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            disabled={!isConnected} // Disable if disconnected
                        />
                        <button
                            onClick={submitTask}
                            className={`px-6 py-2 rounded-lg text-white flex items-center gap-2 ${isConnected ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-400 cursor-not-allowed'}`}
                            disabled={!isConnected}
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
                        id="log-filter"
                        name="log-filter"
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