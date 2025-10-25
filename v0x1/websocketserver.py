import asyncio
import websockets
import json
import threading
from typing import List, Set
from datetime import datetime

class Node:
    def __init__(self, task: str, level: int = 99999) -> None:
        self.task: str = task
        self.parent: bool = False
        self.leaf: bool = False
        self.level: int = level
        self.executionStarted: bool = False
        self.executionSuccess: bool = False
        self.subTasks: List['Node'] = []
        
        # New attributes for enhanced task management
        self.chatresponse: str = None
        self.atomic: bool = False
        self.command: str = None
        self.subtasks: List[str] = []
        self.human_needed: bool = False
        self.human_instructions: List[str] = []

    def to_dict(self):
        """Convert Node to dictionary for JSON serialization"""
        result = {
            "task": self.task,
            "parent": self.parent,
            "leaf": self.leaf,
            "level": self.level,
            "executionStarted": self.executionStarted,
            "executionSuccess": self.executionSuccess,
            "subTasks": [sub.to_dict() for sub in self.subTasks]
        }
        
        # Add optional attributes only if they have values
        if self.chatresponse:
            result["chatresponse"] = self.chatresponse
        if self.atomic:
            result["atomic"] = self.atomic
        if self.command:
            result["command"] = self.command
        if self.subtasks:
            result["subtasks"] = self.subtasks
        if self.human_needed:
            result["human_needed"] = self.human_needed
        if self.human_instructions:
            result["human_instructions"] = self.human_instructions
            
        return result

    def addSubTask(self, subTaskName: str):
        """Add a child node with the given task"""
        child_node = Node(subTaskName, level=(self.level + 1))
        self.subTasks.append(child_node)
        self.parent = True
        return child_node

    def addListOfSubtasks(self, listofsubtasks):
        """Add multiple subtasks at once"""
        if not listofsubtasks:
            return
        for task in listofsubtasks:
            self.subTasks.append(Node(task, level=(self.level + 1)))
        self.parent = True

    def findNodeByTask(self, task_name: str):
        """Recursively find a node by task name"""
        if self.task == task_name:
            return self
        for child in self.subTasks:
            found = child.findNodeByTask(task_name)
            if found:
                return found
        return None

    def __str__(self):
        return str(self.task)


class WebSocketTaskServer:
    def __init__(self, host="localhost", port=8000):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.tree_root: Node = None
        self.lock = threading.Lock()

    def set_tree_root(self, root: Node):
        """Set the root node of the task tree"""
        with self.lock:
            self.tree_root = root

    async def broadcast_tree(self):
        """Broadcast the current tree state to all connected clients"""
        if self.tree_root and self.clients:
            message = json.dumps(self.tree_root.to_dict())
            disconnected_clients = set()
            
            for client in self.clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.add(client)
            
            # Remove disconnected clients
            self.clients -= disconnected_clients

    async def handler(self, websocket):
        """Handle WebSocket connections"""
        self.clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.clients)}")
        
        try:
            # Send initial tree state if available
            if self.tree_root:
                await websocket.send(json.dumps(self.tree_root.to_dict()))
            
            # Keep connection alive and listen for messages
            async for message in websocket:
                # Handle any incoming messages from client if needed
                print(f"Received message: {message}")
                
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            print(f"Client disconnected. Total clients: {len(self.clients)}")

    async def start_server(self):
        """Start the WebSocket server"""
        async with websockets.serve(self.handler, self.host, self.port):
            print(f"WebSocket server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever

    def update_node_status(self, task_name: str, started: bool = None, success: bool = None):
        """Update the execution status of a specific node"""
        with self.lock:
            if self.tree_root:
                node = self.tree_root.findNodeByTask(task_name)
                if node:
                    if started is not None:
                        node.executionStarted = started
                    if success is not None:
                        node.executionSuccess = success
                    
                    # Trigger broadcast in async context
                    asyncio.create_task(self.broadcast_tree())

    def run_in_thread(self):
        """Run the WebSocket server in a separate thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.start_server())


# Global server instance
ws_server = WebSocketTaskServer()


def start_websocket_server_background():
    """Start WebSocket server in background thread"""
    server_thread = threading.Thread(target=ws_server.run_in_thread, daemon=True)
    server_thread.start()
    return ws_server


# Example usage and testing
if __name__ == "__main__":
    # Create a sample tree
    root = Node("Build Web Application", 0)
    root.parent = True
    root.chatresponse = "Starting web application development project"
    
    backend = Node("Backend Development", 1)
    backend.parent = True
    backend.executionStarted = True
    backend.chatresponse = "Backend development in progress"
    
    db_task = Node("Setup Database", 2)
    db_task.leaf = True
    db_task.atomic = True
    db_task.command = "docker run -d postgres:13"
    db_task.executionSuccess = True
    db_task.chatresponse = "Database setup completed successfully"
    
    api_task = Node("Create API Endpoints", 2)
    api_task.leaf = True
    api_task.atomic = True
    api_task.command = "python manage.py startapp api"
    api_task.executionStarted = True
    api_task.human_needed = True
    api_task.human_instructions = ["Verify API endpoints are working", "Test with Postman or curl"]
    
    backend.subTasks = [db_task, api_task]
    
    frontend = Node("Frontend Development", 1)
    frontend.parent = True
    frontend.subtasks = ["Design UI Components", "Implement routing", "Add state management"]
    
    ui_task = Node("Design UI Components", 2)
    ui_task.leaf = True
    ui_task.atomic = True
    ui_task.command = "npm run generate-components"
    
    frontend.subTasks = [ui_task]
    
    root.subTasks = [backend, frontend]
    
    # Set the tree and start server
    ws_server.set_tree_root(root)
    
    print("Starting WebSocket server...")
    asyncio.run(ws_server.start_server())