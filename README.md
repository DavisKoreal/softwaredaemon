# Task Tree Visualizer Integration

This system provides a real-time task tree visualization with WebSocket communication between a Python backend and Next.js frontend.

## Components

### Frontend (task-tree-visualizer/)
- **Next.js 13+** application with React components
- **WebSocket client** that connects to the Python backend
- **Real-time visualization** of hierarchical task trees
- **Interactive UI** with collapsible task details

### Backend (v0x1/)
- **Python WebSocket server** for broadcasting task updates
- **AI-powered task decomposition** using DeepSeek API
- **Real-time task execution** with status updates
- **Enhanced task attributes** (atomic, commands, human instructions)

## Quick Start

### Option 1: Demo Mode (Recommended for testing)
```powershell
# Run the demo with sample data
.\start_demo.ps1
```

This will:
1. Start the Next.js frontend on `http://localhost:3000`
2. Start the WebSocket server on `ws://localhost:8000` with sample data
3. Simulate task execution with status updates

### Option 2: Full AI Mode
```powershell
# Terminal 1: Start the frontend
cd task-tree-visualizer
npm install
npm run dev

# Terminal 2: Start the AI daemon
cd v0x1
python 0x1daemon.py
```

## New Features

### Enhanced Node Attributes
Each task now supports:
- **`chatresponse`**: AI-generated comments about the task
- **`atomic`**: Boolean indicating if task is executable
- **`command`**: Shell command for atomic tasks
- **`subtasks`**: List of subtask descriptions
- **`human_needed`**: Boolean for human intervention requirements
- **`human_instructions`**: List of instructions for human users

### Frontend Enhancements
- **Collapsible details**: Atomic tasks can be expanded to show commands and responses
- **Visual indicators**: Color-coded status for execution states
- **Human intervention alerts**: Special highlighting for tasks requiring human input
- **Real-time updates**: Live WebSocket connection for instant status updates

## File Structure
```
task-tree-visualizer/          # Next.js Frontend
├── src/app/page.tsx          # Main visualization component
├── package.json              # Frontend dependencies
└── ...

v0x1/                         # Python Backend  
├── 0x1daemon.py             # Main AI daemon with WebSocket
├── websocketserver.py       # Standalone WebSocket server
├── test_websocket.py        # Demo script with sample data
├── task.txt                 # Input task description
└── ...

start_demo.ps1               # Quick start script
```

## WebSocket Protocol

### Data Format
```json
{
  "task": "Task name",
  "parent": true/false,
  "leaf": true/false, 
  "level": 0,
  "executionStarted": true/false,
  "executionSuccess": true/false,
  "subTasks": [...],
  "chatresponse": "AI response",
  "atomic": true/false,
  "command": "shell command",
  "subtasks": ["sub1", "sub2"],
  "human_needed": true/false,
  "human_instructions": ["instruction1", "instruction2"]
}
```

### Connection
- **URL**: `ws://localhost:8000/ws`
- **Protocol**: JSON messages
- **Updates**: Real-time tree state broadcasts

## Usage Examples

### 1. Simple Task
Edit `v0x1/task.txt`:
```
Create a simple HTML website with a contact form
```

### 2. Complex Task  
```
Build a REST API with authentication, database integration, and documentation
```

### 3. Development Task
```
Set up a React application with TypeScript, routing, and testing framework
```

## Troubleshooting

### Frontend Issues
- Ensure Node.js is installed: `node --version`
- Install dependencies: `npm install`
- Check port 3000 is available

### Backend Issues  
- Install Python dependencies: `pip install websockets openai python-dotenv`
- Set DeepSeek API key in `.env` file
- Check port 8000 is available

### Connection Issues
- Verify WebSocket server is running on port 8000
- Check browser console for connection errors
- Ensure firewall allows localhost connections

## Development

### Adding New Task Attributes
1. Update the `Node` class in both `0x1daemon.py` and `websocketserver.py`
2. Modify the `to_dict()` method to include new attributes
3. Update the frontend `Node` interface in `page.tsx`
4. Add visualization for new attributes in the `TaskNode` component

### Customizing AI Responses
- Edit `systemPrompt.py` to modify AI behavior
- Adjust the JSON response format in `getSubTaskList()`
- Update task classification logic in `fillTreeWithTasks()`

## API Keys

Create a `.env` file in the `v0x1/` directory:
```
DEEPSEEK_API_KEY=your_api_key_here
```

Get your API key from [DeepSeek Platform](https://platform.deepseek.com/).