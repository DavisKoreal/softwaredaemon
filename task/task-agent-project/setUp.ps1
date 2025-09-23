# Modern UI Enhancement Script for Task Agent
# This script updates the React components with modern design patterns

# Function to write file content
function Write-FileContent {
    param(
        [string]$FilePath,
        [string]$Content
    )
    Set-Content -Path $FilePath -Value $Content -Encoding UTF8
    Write-Host "Updated: $FilePath" -ForegroundColor Green
}

# Enhanced App.tsx with modern UI
$AppTsxContent = @'
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
      case 'success': return '✅';
      case 'error': return '❌';
      case 'warning': return '⚠️';
      default: return 'ℹ️';
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
                <span className="mr-2">🎯</span>
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
                      <span>🚀</span>
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
                  <span className="mr-2">📋</span>
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
                        <div className="text-6xl mb-4">📝</div>
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
'@

# Enhanced App.css with modern animations
$AppCssContent = @'
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  margin: 0;
  padding: 0;
  background: #f8fafc;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Smooth animations */
* {
  transition: all 0.2s ease;
}

/* Pulse animation for connection status */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Gradient text effect */
.bg-clip-text {
  -webkit-background-clip: text;
  background-clip: text;
}

/* Card hover effects */
.shadow-xl {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Focus styles */
textarea:focus,
input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* Button animations */
button:not(:disabled):hover {
  transform: translateY(-1px);
}

button:not(:disabled):active {
  transform: translateY(0);
}

/* Log entry animations */
.log-entry {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Loading spinner */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Glass morphism effect */
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Responsive design improvements */
@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }
  
  h1 {
    font-size: 2rem;
  }
}
'@

# Enhanced package.json with additional dependencies
$PackageJsonContent = @'
{
  "name": "task-agent-ui",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite --host 0.0.0.0",
    "build": "tsc && vite build",
    "preview": "vite preview --host 0.0.0.0",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "ws": "^8.18.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.15",
    "@types/react-dom": "^18.2.7",
    "@types/ws": "^8.5.5",
    "@vitejs/plugin-react": "^4.0.3",
    "autoprefixer": "^10.4.14",
    "postcss": "^8.4.27",
    "tailwindcss": "^3.3.3",
    "typescript": "^5.0.2",
    "vite": "^4.4.5"
  }
}
'@

# Enhanced index.html with better meta tags and font loading
$IndexHtmlContent = @'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="Task Agent Control Center - Manage and monitor your automated tasks" />
  <meta name="theme-color" content="#4f46e5" />
  <title>Task Agent Control Center</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    /* Loading screen */
    #loading {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 9999;
      transition: opacity 0.5s ease;
    }
    
    .loading-spinner {
      width: 50px;
      height: 50px;
      border: 3px solid rgba(255,255,255,0.3);
      border-radius: 50%;
      border-top-color: #fff;
      animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  </style>
</head>
<body>
  <div id="loading">
    <div class="loading-spinner"></div>
  </div>
  <div id="root"></div>
  <script type="module" src="/src/main.tsx"></script>
  <script>
    // Hide loading screen when page loads
    window.addEventListener('load', () => {
      const loading = document.getElementById('loading');
      if (loading) {
        loading.style.opacity = '0';
        setTimeout(() => loading.remove(), 500);
      }
    });
  </script>
</body>
</html>
'@

# Enhanced Tailwind config with custom animations
$TailwindConfigContent = @'
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'bounce-in': 'bounceIn 0.6s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateX(-10px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        bounceIn: {
          '0%': { opacity: '0', transform: 'scale(0.3)' },
          '50%': { opacity: '1', transform: 'scale(1.05)' },
          '70%': { transform: 'scale(0.9)' },
          '100%': { transform: 'scale(1)' },
        },
      },
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        }
      }
    },
  },
  plugins: [],
}
'@

# Write all the enhanced files
Write-Host "🚀 Starting UI Modernization..." -ForegroundColor Cyan
Write-Host ""

try {
    # Update React components
    Write-FileContent -FilePath "ui/src/App.tsx" -Content $AppTsxContent
    Write-FileContent -FilePath "ui/src/App.css" -Content $AppCssContent
    Write-FileContent -FilePath "ui/package.json" -Content $PackageJsonContent
    Write-FileContent -FilePath "ui/index.html" -Content $IndexHtmlContent
    Write-FileContent -FilePath "ui/tailwind.config.js" -Content $TailwindConfigContent

    Write-Host ""
    Write-Host "✅ UI Modernization Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎨 New Features Added:" -ForegroundColor Yellow
    Write-Host "  • Modern gradient background and glassmorphism effects"
    Write-Host "  • Enhanced status indicators with animations"
    Write-Host "  • Improved task submission form with textarea"
    Write-Host "  • Categorized log entries with color coding and icons"
    Write-Host "  • Auto-reconnection with exponential backoff"
    Write-Host "  • Responsive design for mobile devices"
    Write-Host "  • Loading states and smooth transitions"
    Write-Host "  • Auto-scrolling logs and clear functionality"
    Write-Host "  • Better typography with Inter font"
    Write-Host "  • Loading screen for better UX"
    Write-Host ""
    Write-Host "🔄 Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. cd ui"
    Write-Host "  2. npm install  # Install new dependencies"
    Write-Host "  3. npm run dev  # Start development server"
    Write-Host ""
    Write-Host "The UI will be available at http://localhost:5173" -ForegroundColor Magenta

} catch {
    Write-Host "❌ Error during modernization: $_" -ForegroundColor Red
    exit 1
}