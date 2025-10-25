// app/page.tsx
'use client';

// Import React hooks for managing state and side effects
import { useEffect, useState } from 'react';
// Import Lucide React icons for UI elements like chevrons, checkmarks, circles, and loaders
import { ChevronRight, ChevronDown, CheckCircle2, Circle, Loader2, Play } from 'lucide-react';

/**
 * Interface defining the structure of a task node in the tree.
 * Each node represents a task with metadata about its execution state and hierarchy.
 */
interface Node {
  task: string;                // The name/description of the task
  parent: boolean;             // Flag indicating if this node is a parent (has subtasks)
  leaf: boolean;               // Flag indicating if this node is a leaf (no subtasks)
  level: number;               // Hierarchical level/depth in the tree (root is 0)
  executionStarted: boolean;   // Flag indicating if execution has begun for this task
  executionSuccess: boolean;   // Flag indicating if execution completed successfully
  
  subTasks: Node[];            // Array of child/sub-task nodes
  
  // New attributes for enhanced task management
  chatresponse?: string;       // Comments or response from the system
  atomic?: boolean;            // Flag indicating if this is an atomic task
  command?: string;            // Command to execute if atomic
  subtasks?: string[];         // List of subtask strings if not atomic
  human_needed?: boolean;      // Flag indicating if human intervention is required
  human_instructions?: string[]; // Instructions for the human user if needed
}

/**
 * Sample task tree data for demonstration purposes.
 */
const sampleTreeData: Node = {
  task: "Initialize Project",
  parent: true,
  leaf: false,
  level: 0,
  executionStarted: true,
  executionSuccess: false,
  subTasks: [
    {
      task: "Setup Environment",
      parent: true,
      leaf: false,
      level: 1,
      executionStarted: true,
      executionSuccess: true,
      subTasks: [
        {
          task: "Install Dependencies",
          parent: false,
          leaf: true,
          level: 2,
          executionStarted: true,
          executionSuccess: true,
          subTasks: [],
          atomic: true,
          command: "npm install",
          chatresponse: "Successfully installed all required packages"
        },
        {
          task: "Configure Database",
          parent: false,
          leaf: true,
          level: 2,
          executionStarted: false,
          executionSuccess: false,
          subTasks: [],
          atomic: true,
          command: "docker run -d postgres",
          human_needed: true,
          human_instructions: ["Please ensure Docker is running", "Verify database credentials"]
        }
      ]
    },
    {
      task: "Develop Features",
      parent: true,
      leaf: false,
      level: 1,
      executionStarted: false,
      executionSuccess: false,
      subTasks: [
        {
          task: "Implement Authentication",
          parent: false,
          leaf: true,
          level: 2,
          executionStarted: false,
          executionSuccess: false,
          subTasks: []
        },
        {
          task: "Build Dashboard",
          parent: false,
          leaf: true,
          level: 2,
          executionStarted: false,
          executionSuccess: false,
          subTasks: []
        }
      ]
    },
    {
      task: "Testing",
      parent: false,
      leaf: true,
      level: 1,
      executionStarted: false,
      executionSuccess: false,
      subTasks: []
    }
  ]
};

/**
 * Main component for the Task Tree Visualizer.
 * This component handles WebSocket connection for real-time data updates
 * and renders the hierarchical task tree with status indicators.
 */
export default function TaskTreeVisualizer() {
  // State to hold the current tree data received from WebSocket
  const [treeData, setTreeData] = useState<Node | null>(null);
  // State to hold the active WebSocket instance
  const [ws, setWs] = useState<WebSocket | null>(null);
  // State tracking the WebSocket connection status (disconnected, connecting, connected)
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');
  // State for the WebSocket URL, defaulting to localhost
  const [wsUrl, setWsUrl] = useState('ws://localhost:8000/ws');

  /**
   * Function to establish a WebSocket connection.
   * Sets up event handlers for open, message, error, and close events.
   * Parses incoming JSON messages and updates the tree data state.
   */
  const connectWebSocket = () => {
    // Update status to indicate connection attempt in progress
    setConnectionStatus('connecting');
    // Create new WebSocket instance with the configured URL
    const websocket = new WebSocket(wsUrl);

    // Event handler for successful connection
    websocket.onopen = () => {
      console.log('WebSocket connected');
      setConnectionStatus('connected');
    };

    // Event handler for incoming messages
    websocket.onmessage = (event) => {
      try {
        // Parse the JSON data from the message and update the tree state
        const data = JSON.parse(event.data);
        setTreeData(data);
      } catch (error) {
        // Log any parsing errors without crashing the app
        console.error('Error parsing message:', error);
      }
    };

    // Event handler for connection errors
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      // Mark connection as failed
      setConnectionStatus('disconnected');
    };

    // Event handler for connection closure
    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      // Mark connection as closed
      setConnectionStatus('disconnected');
    };

    // Store the WebSocket instance in state for later management
    setWs(websocket);
  };

  /**
   * Function to close the active WebSocket connection.
   * Clears the instance from state after closing.
   */
  const disconnect = () => {
    if (ws) {
      // Close the connection if it exists
      ws.close();
      setWs(null);
    }
  };

  /**
   * Effect hook for cleanup on unmount or WebSocket change.
   * Ensures the WebSocket is properly closed to prevent leaks.
   */
  useEffect(() => {
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [ws]);  // Dependency on ws to re-run on changes

  /**
   * Effect hook to load sample data on initial render.
   */
  useEffect(() => {
    setTreeData(sampleTreeData);
  }, []);

  return (
    // Main container with a gradient background and padding
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
      {/* Centered content wrapper with max width */}
      <div className="max-w-6xl mx-auto">
        {/* Header section with title and subtitle */}
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Task Tree Visualizer</h1>
          <p className="text-purple-200">Real-time task execution monitoring</p>
        </header>

        {/* WebSocket connection control panel with backdrop blur effect */}
        <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6 mb-6 border border-white/20">
          <div className="flex gap-4 items-end">
            {/* Input section for WebSocket URL */}
            <div className="flex-1">
              <label className="block text-sm font-medium text-purple-200 mb-2">
                WebSocket URL
              </label>
              <input
                type="text"
                value={wsUrl}
                onChange={(e) => setWsUrl(e.target.value)}  // Update URL state on input change
                className="w-full px-4 py-2 bg-white/10 border border-white/30 rounded-lg text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="ws://localhost:8000/ws"
                // Disable input while connected to prevent changes mid-session
                disabled={connectionStatus !== 'disconnected'}
              />
            </div>
            {/* Connect/Disconnect button with dynamic styling and text */}
            <button
              onClick={connectionStatus === 'disconnected' ? connectWebSocket : disconnect}
              className={`px-6 py-2 rounded-lg font-medium transition-all ${
                // Conditional classes based on connection status
                connectionStatus === 'connected'
                  ? 'bg-red-500 hover:bg-red-600 text-white'
                  : connectionStatus === 'connecting'
                  ? 'bg-yellow-500 text-white cursor-not-allowed'
                  : 'bg-purple-600 hover:bg-purple-700 text-white'
              }`}
              // Disable button during connection attempt
              disabled={connectionStatus === 'connecting'}
            >
              {/* Dynamic button text based on status */}
              {connectionStatus === 'connected' ? 'Disconnect' : connectionStatus === 'connecting' ? 'Connecting...' : 'Connect'}
            </button>
            {/* Load Sample Data button */}
            <button
              onClick={() => setTreeData(sampleTreeData)}
              className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-all"
            >
              Load Sample Data
            </button>
          </div>
          {/* Status indicator dot and text */}
          <div className="mt-3 flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${
              // Color-coded dot based on status
              connectionStatus === 'connected' ? 'bg-green-400' : 
              connectionStatus === 'connecting' ? 'bg-yellow-400' : 
              'bg-red-400'
            }`} />
            <span className="text-sm text-purple-200">
              {/* Dynamic status text */}
              {connectionStatus === 'connected' ? 'Connected' : 
               connectionStatus === 'connecting' ? 'Connecting...' : 
               'Disconnected'}
            </span>
          </div>
        </div>

        {/* Main tree display container with backdrop blur */}
        <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20">
          {treeData ? (
            // Render the tree if data is available
            <TaskNode node={treeData} />
          ) : (
            // Placeholder message based on connection status
            <div className="text-center py-12 text-purple-300">
              {connectionStatus === 'connected' 
                ? 'Waiting for data...' 
                : 'Connect to WebSocket to view task tree'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Recursive sub-component for rendering a single task node and its children.
 * Handles expansion/collapse for parent nodes and status visualization.
 * @param {Object} props - Component props
 * @param {Node} props.node - The task node data
 * @param {number} [props.depth=0] - Current depth level for indentation
 */
function TaskNode({ node, depth = 0 }: { node: Node; depth?: number }) {
  // Local state for toggling expansion of parent nodes and atomic task details
  const [expanded, setExpanded] = useState(true);
  const [detailsExpanded, setDetailsExpanded] = useState(false);
  // Check if node has subtasks (is a parent)
  const hasSubTasks = node.subTasks && node.subTasks.length > 0;
  // Check if node has expandable details (atomic tasks or additional info)
  const hasExpandableDetails = node.atomic || node.chatresponse || node.human_needed;

  /**
   * Helper function to return the appropriate icon based on execution status.
   * - Success: Checkmark
   * - Started: Spinning loader
   * - Pending: Empty circle
   */
  const getStatusIcon = () => {
    if (node.executionSuccess) {
      return <CheckCircle2 className="w-5 h-5 text-green-400" />;
    }
    if (node.executionStarted) {
      return <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />;
    }
    return <Circle className="w-5 h-5 text-gray-400" />;
  };

  /**
   * Helper function to return background/border classes based on execution status.
   * Applies subtle colored overlays for visual feedback.
   */
  const getStatusColor = () => {
    if (node.executionSuccess) return 'bg-green-500/20 border-green-500/50';
    if (node.executionStarted) return 'bg-blue-500/20 border-blue-500/50';
    return 'bg-gray-500/20 border-gray-500/50';
  };

  return (
    // Container for the node with indentation based on depth
    <div className="space-y-2" style={{ marginLeft: depth > 0 ? '24px' : '0' }}>
      {/* Node row with status icon, task name, and metadata */}
      <div
        className={`flex items-center gap-3 p-3 rounded-lg border ${getStatusColor()} transition-all hover:bg-white/5`}
      >
        {/* Expand/collapse button for parents */}
        {hasSubTasks && (
          <button
            onClick={() => setExpanded(!expanded)}  // Toggle expansion state
            className="text-purple-200 hover:text-white transition-colors"
          >
            {expanded ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>
        )}
        {/* Spacer for leaf nodes (no button) */}
        {!hasSubTasks && <div className="w-4" />}
        
        {/* Status icon */}
        {getStatusIcon()}
        
        {/* Task details section */}
        <div className="flex-1">
          <div className="text-white font-medium">{node.task}</div>
          {/* Metadata row with level and flags */}
          <div className="text-sm text-purple-300 flex gap-4 mt-1">
            <span>Level: {node.level}</span>
            {node.parent && <span className="text-yellow-400">Parent</span>}
            {node.leaf && <span className="text-blue-400">Leaf</span>}
            {node.atomic && <span className="text-orange-400">Atomic</span>}
            {node.human_needed && <span className="text-red-400">Human Required</span>}
          </div>
        </div>

        {/* Details toggle button for atomic tasks or tasks with additional info */}
        {hasExpandableDetails && (
          <button
            onClick={() => setDetailsExpanded(!detailsExpanded)}
            className="text-purple-200 hover:text-white transition-colors p-1"
            title="Toggle task details"
          >
            <Play className={`w-4 h-4 transition-transform ${detailsExpanded ? 'rotate-90' : ''}`} />
          </button>
        )}
      </div>

      {/* Expandable details section for atomic tasks and additional info */}
      {hasExpandableDetails && detailsExpanded && (
        <div className="ml-8 mt-2 p-3 bg-white/5 rounded-lg border border-white/10">
          {/* Chat response */}
          {node.chatresponse && (
            <div className="mb-3">
              <div className="text-xs text-purple-300 font-semibold mb-1">Response:</div>
              <div className="text-sm text-white bg-blue-500/20 p-2 rounded border border-blue-500/30">
                {node.chatresponse}
              </div>
            </div>
          )}

          {/* Atomic command */}
          {node.atomic && node.command && (
            <div className="mb-3">
              <div className="text-xs text-purple-300 font-semibold mb-1">Command:</div>
              <div className="text-sm text-white bg-gray-500/20 p-2 rounded border border-gray-500/30 font-mono">
                {node.command}
              </div>
            </div>
          )}

          {/* Subtasks list (for non-atomic tasks) */}
          {!node.atomic && node.subtasks && node.subtasks.length > 0 && (
            <div className="mb-3">
              <div className="text-xs text-purple-300 font-semibold mb-1">Subtasks:</div>
              <ul className="text-sm text-white space-y-1">
                {node.subtasks.map((subtask, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <Circle className="w-3 h-3 text-purple-300 mt-0.5 flex-shrink-0" />
                    <span>{subtask}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Human instructions */}
          {node.human_needed && node.human_instructions && node.human_instructions.length > 0 && (
            <div>
              <div className="text-xs text-red-300 font-semibold mb-1">Human Instructions:</div>
              <ul className="text-sm text-white space-y-1">
                {node.human_instructions.map((instruction, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <div className="w-3 h-3 bg-red-400 rounded-full mt-0.5 flex-shrink-0"></div>
                    <span className="text-red-100">{instruction}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Render subtasks if expanded and present */}
      {hasSubTasks && expanded && (
        <div className="relative ml-6">
          {/* Vertical line connecting subtasks */}
          <div className="absolute left-0 top-0 bottom-0 w-px bg-white/20"></div>
          <div className="space-y-2">
            {/* Recursively render each subtask with increased depth */}
            {node.subTasks.map((subTask, index) => (
              <div key={index} className="relative">
                {/* Horizontal line connecting to subtask */}
                <div className="absolute left-0 top-1/2 w-4 h-px bg-white/20 transform -translate-y-1/2"></div>
                <TaskNode node={subTask} depth={depth + 1} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}