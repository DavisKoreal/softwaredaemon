# Modified daemon.py with WebSocket integration
from openai import OpenAI
import json
import time
import shellinteractions
from typing import List
import os
import sys
from dotenv import load_dotenv
from systemPrompt import sysRole
import sqlite3
import asyncio
import threading
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# Import WebSocket server components
import websockets
from datetime import datetime

# Database class (unchanged)
class Database:
    def __init__(self, db_name="taskagent.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS chat_history (
                                    id INTEGER PRIMARY KEY,
                                    input_task TEXT,
                                    response TEXT,
                                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                                )''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS terminal_execution_history (
                                    id INTEGER PRIMARY KEY,
                                    command TEXT,
                                    response TEXT,
                                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                                )''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS tasks_tree (
                                    id INTEGER PRIMARY KEY,
                                    task TEXT,
                                    parent_id INTEGER,
                                    level INTEGER,
                                    FOREIGN KEY(parent_id) REFERENCES tasks_tree(id)
                                )''')

    def log_chat(self, input_task, response):
        with self.conn:
            self.conn.execute('INSERT INTO chat_history (input_task, response) VALUES (?, ?)', (input_task, response))

    def log_terminal_execution(self, command, response):
        with self.conn:
            self.conn.execute('INSERT INTO terminal_execution_history (command, response) VALUES (?, ?)', (command, response))

    def log_task(self, task, parent_id, level):
        with self.conn:
            self.conn.execute('INSERT INTO tasks_tree (task, parent_id, level) VALUES (?, ?, ?)', (task, parent_id, level))


# WebSocket Server Integration
class WebSocketTaskServer:
    def __init__(self, host="localhost", port=8000):
        self.host = host
        self.port = port
        self.clients = set()
        self.tree_root = None
        self.loop = None

    def set_tree_root(self, root):
        """Set the root node of the task tree"""
        self.tree_root = root

    async def broadcast_tree(self):
        """Broadcast the current tree state to all connected clients"""
        if self.tree_root and self.clients:
            message = json.dumps(self.tree_root.to_dict(), indent=2)
            disconnected_clients = set()
            
            websocket_logger.debug(f"Broadcasting to {len(self.clients)} clients")
            
            for client in self.clients:
                try:
                    await client.send(message)
                    websocket_logger.debug("Successfully sent message to client")
                except Exception as e:
                    websocket_logger.error(f"Error broadcasting to client: {e}")
                    disconnected_clients.add(client)
            
            if disconnected_clients:
                self.clients -= disconnected_clients
                websocket_logger.info(f"Removed {len(disconnected_clients)} disconnected clients")

    async def handler(self, websocket):
        """Handle WebSocket connections"""
        client_addr = websocket.remote_address
        self.clients.add(websocket)
        websocket_logger.info(f"Client connected from {client_addr}. Total clients: {len(self.clients)}")
        
        try:
            if self.tree_root:
                initial_message = json.dumps(self.tree_root.to_dict(), indent=2)
                await websocket.send(initial_message)
                websocket_logger.debug("Sent initial tree data to new client")
            
            async for message in websocket:
                websocket_logger.debug(f"Received message from client {client_addr}: {message}")
                # Handle any incoming messages from client if needed
                
        except websockets.exceptions.ConnectionClosed:
            websocket_logger.info(f"Client {client_addr} connection closed normally")
        except Exception as e:
            websocket_logger.error(f"Error in WebSocket handler for {client_addr}: {e}")
        finally:
            if websocket in self.clients:
                self.clients.remove(websocket)
            websocket_logger.info(f"Client {client_addr} disconnected. Total clients: {len(self.clients)}")

    async def start_server(self):
        """Start the WebSocket server"""
        websocket_logger.info(f"Starting WebSocket server on ws://{self.host}:{self.port}")
        try:
            async with websockets.serve(self.handler, self.host, self.port):
                websocket_logger.info(f"WebSocket server successfully started on ws://{self.host}:{self.port}")
                await asyncio.Future()
        except Exception as e:
            websocket_logger.error(f"Failed to start WebSocket server: {e}")
            raise

    def run_in_thread(self):
        """Run the WebSocket server in a separate thread"""
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            websocket_logger.info("WebSocket server thread started")
            self.loop.run_until_complete(self.start_server())
        except Exception as e:
            websocket_logger.error(f"Error in WebSocket server thread: {e}")
            raise

    def update_and_broadcast(self):
        """Schedule a broadcast in the event loop"""
        if self.loop and self.loop.is_running():
            try:
                asyncio.run_coroutine_threadsafe(self.broadcast_tree(), self.loop)
                websocket_logger.debug("Scheduled tree broadcast")
            except Exception as e:
                websocket_logger.error(f"Error scheduling broadcast: {e}")


# Global WebSocket server
ws_server = WebSocketTaskServer()


# Load environment variables
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def setup_logging():
    """Configure logging for production use"""
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # File handler for all logs (rotates daily, keeps 30 days)
    file_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'daemon.log'),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Error file handler for errors only (rotates at 10MB, keeps 5 files)
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'daemon_errors.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # WebSocket specific handler
    websocket_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'websocket.log'),
        when='midnight',
        interval=1,
        backupCount=7,  # Keep 7 days of WebSocket logs
        encoding='utf-8'
    )
    websocket_handler.setLevel(logging.DEBUG)
    websocket_handler.setFormatter(detailed_formatter)
    
    # Add handlers to root logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    # Create WebSocket logger
    ws_logger = logging.getLogger('websocket')
    ws_logger.addHandler(websocket_handler)
    ws_logger.setLevel(logging.DEBUG)
    
    # Create task processing logger
    task_logger = logging.getLogger('task_processing')
    task_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'task_processing.log'),
        when='midnight',
        interval=1,
        backupCount=14,  # Keep 2 weeks of task logs
        encoding='utf-8'
    )
    task_handler.setLevel(logging.DEBUG)
    task_handler.setFormatter(detailed_formatter)
    task_logger.addHandler(task_handler)
    task_logger.setLevel(logging.DEBUG)
    
    return logger

# Initialize logging
logger = setup_logging()
websocket_logger = logging.getLogger('websocket')
task_logger = logging.getLogger('task_processing')

print("The API key is: " + DEEPSEEK_API_KEY)

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
database = Database()

chatHistory = [{"inputTask": " ", "response": " "}]
terminalExecutionHistory = [{"command": " ", "response": " "}]


def getTabsBasedOnLevel(n):
    return "\t" * n


def logComputationToFile(logMessage):
    """Log computation messages using proper logging"""
    task_logger.info(logMessage)
    
    # Also log to the old file for backward compatibility
    log_file = os.path.join("taskagent.log")
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(time.asctime() + " : " + logMessage + "\n")
    except Exception as e:
        logger.error(f"Failed to write to legacy log file: {e}")


def getSubTaskList(inputTask="Say Hello"):
    logger.info(f"Generating sub task list for task: {inputTask}")
    chatHistoryString = "\n".join(str(item) for item in chatHistory)

    full_sysRole = sysRole + """ and the following is the chat history """ + chatHistoryString

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": full_sysRole},
                {"role": "user", "content": "The input task is :" + inputTask},
            ],
            stream=False
        )
        
        # check response for errors
        if not response or not response.choices:
            logger.error("No response from the API")
            return {"atomic": "true", "command": inputTask, "subtasks": []}
        
        response_content = response.choices[0].message.content
        logger.debug(f"API Response: {response_content}")
        
        chatHistory.append({"inputTask": inputTask, "response": response_content})
        logComputationToFile("Response from the API: " + response_content)
        
        # Parse JSON response
        jsonform = json.loads(response_content.replace("```json", "").replace("```", ""))
        logger.info(f"Parsed task breakdown - Atomic: {jsonform.get('atomic')}, Subtasks: {len(jsonform.get('subtasks', []))}")
        
        return jsonform
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        return {"atomic": "true", "command": inputTask, "subtasks": []}
    except Exception as e:
        logger.error(f"Error calling API: {e}")
        return {"atomic": "true", "command": inputTask, "subtasks": []}


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
        child_node = Node(subTaskName, level=(self.level + 1))
        self.subTasks.append(child_node)
        self.parent = True
        return child_node

    def addListOfSubtasks(self, listofsubtasks):
        logComputationToFile("adding a list of subtasks of the task: " + self.task)
        if not listofsubtasks:
            return
        for task in listofsubtasks:
            self.subTasks.append(Node(task, level=(self.level + 1)))
        self.parent = True

    def fillTreeWithTasks(self):
        response = getSubTaskList(self.task)
        
        # Store the chat response
        self.chatresponse = f"Task breakdown completed. Atomic: {response['atomic']}"

        if response["atomic"] == "false":
            self.atomic = False
            self.subtasks = response["subtasks"] if "subtasks" in response else []
            self.addListOfSubtasks(response["subtasks"])
            logComputationToFile("The task is not atomic, so we need to add the subtasks of the task: " + self.task)
            
            # Broadcast tree update after adding subtasks
            ws_server.update_and_broadcast()
            
            for childTask in self.subTasks:
                childTask.fillTreeWithTasks()

        if response["atomic"] == "true":
            self.atomic = True
            self.leaf = True
            self.command = response["command"]
            
            # Check if human intervention is needed (simple heuristic)
            command_lower = response["command"].lower()
            if any(keyword in command_lower for keyword in ["install", "setup", "configure", "manual", "open"]):
                self.human_needed = True
                self.human_instructions = [
                    f"Please execute the command: {response['command']}",
                    "Verify the operation completed successfully",
                    "Check for any error messages or prompts"
                ]
            
            # Keep original task name, store command separately
            # self.task remains the same, command is stored in self.command
            
            # Broadcast tree update after marking as leaf
            ws_server.update_and_broadcast()

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


class NaryTree:
    def __init__(self, root_task=None, startlevel=0):
        self.root = Node(root_task, level=startlevel) if root_task is not None else None

    def postorder_traversal(self, node=None):
        if node is None and self.root is None:
            return []

        if node is None:
            node = self.root

        result = []
        if node.parent:
            logComputationToFile(getTabsBasedOnLevel(node.level) + "PARENT TASK: " + str(node.task))
            for child in node.subTasks:
                logComputationToFile(getTabsBasedOnLevel(child.level) + "The task of the child node: " + str(child.task))
                result.extend(self.postorder_traversal(child))

        if not node.parent:
            logComputationToFile(getTabsBasedOnLevel(node.level) + "LEAF TASK: " + str(node.task))
            result.append(node.task)

        return result


if __name__ == "__main__":
    logger.info("Starting Task Agent Daemon")
    
    # Start WebSocket server in background
    logger.info("Initializing WebSocket server...")
    server_thread = threading.Thread(target=ws_server.run_in_thread, daemon=True)
    server_thread.start()
    logger.info("WebSocket server thread started, waiting for initialization...")
    time.sleep(2)  # Give server time to start
    
    continueExecution = input("Do you want to continue execution? (y/n): ")
    while continueExecution.lower() != 'y':
        logger.debug("Waiting for user confirmation to continue...")
        time.sleep(10)
        continueExecution = input("Do you want to continue execution? (y/n): ")

    # Read root task from file
    logger.info("Reading root task from task.txt...")
    try:
        with open("task.txt", "r") as file:
            rootTask = file.read().strip()
        logger.info(f"Root task loaded: {rootTask}")
    except FileNotFoundError:
        logger.error("task.txt file not found")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading task.txt: {e}")
        sys.exit(1)

    # Create tree and set as WebSocket root
    logger.info("Creating task tree structure...")
    tree = NaryTree(root_task=rootTask)
    ws_server.set_tree_root(tree.root)
    ws_server.update_and_broadcast()
    
    daemon = shellinteractions.ShellInteractions()
    
    # Fill tree with tasks (this will broadcast updates)
    logger.info("Building task tree with AI decomposition...")
    try:
        tree.root.fillTreeWithTasks()
        logger.info("Task tree construction completed")
    except Exception as e:
        logger.error(f"Error building task tree: {e}")
        sys.exit(1)
    
    stepsTaken = tree.postorder_traversal()
    logger.info(f"Task execution plan created with {len(stepsTaken)} steps")

    # Execute tasks and update status
    for i, step in enumerate(stepsTaken, 1):
        logger.info(f"Executing step {i}/{len(stepsTaken)}: {step}")
        # log the command that is being implemented in this step
        # lo
        # Find the node and mark as started
        node = tree.root.findNodeByTask(step)
        if node:
            node.executionStarted = True
            ws_server.update_and_broadcast()
            logger.debug(f"Marked task as started: {step}")
        
        logComputationToFile("Executing the command: " + step)
        
        try:
            shellexecutionresult = daemon.executeCommand(step)
            logger.info(f"Command executed successfully: {step}")
            logger.debug(f"Command output: {shellexecutionresult}")
            
            # Mark as completed
            if node:
                node.executionSuccess = True
                ws_server.update_and_broadcast()
                logger.debug(f"Marked task as completed: {step}")
            
        except Exception as e:
            logger.error(f"Error executing command '{step}': {e}")
            # Mark as failed but continue
            if node:
                node.executionSuccess = False
                ws_server.update_and_broadcast()
        
        logComputationToFile("The result of the command: " + shellexecutionresult + " \n")
        terminalExecutionHistory.append({"command": step, "response": shellexecutionresult})
        
        time.sleep(0.5)  # Small delay to see updates
    
    logger.info("All tasks completed!")
    logger.info("WebSocket server still running. Press Ctrl+C to exit.")
    
    # Keep main thread alive to keep WebSocket server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutdown signal received, stopping daemon...")
    finally:
        logger.info("Task Agent Daemon stopped")