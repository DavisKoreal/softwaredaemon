import asyncio
import http.server
import socketserver
import websockets
import json
import time
import os
import sys
import subprocess
from typing import List
from openai import OpenAI
from dotenv import load_dotenv
import threading
import watchfiles

# Load environment variables from .env file
load_dotenv()

# Set the OpenAI API key and base URL
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
print("The API key is: " + DEEPSEEK_API_KEY)
if not DEEPSEEK_API_KEY:
    print("Error: DEEPSEEK_API_KEY not found in .env file")
    sys.exit(1)

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

chatHistory = [{"inputTask": " ", "response": " "}]
terminalExecutionHistory = [{"command": " ", "response": " "}]

def getdirectoryHistory():
    print("Getting the directory history")

def getTabsBasedOnLevel(n):
    return "\t" * n

async def broadcast_log_async(log_entry):
    if connected_clients:
        await asyncio.gather(*(client.send(log_entry) for client in connected_clients))

def logComputationToFile(logMessage):
    log_file = os.path.join("taskagent.log")
    with open(log_file, 'a', encoding='utf-8') as f:
        log_entry = f"{time.asctime()} : {logMessage}\n"
        f.write(log_entry)
        # Broadcast in async context only if loop is running
        if connected_clients and asyncio.get_event_loop().is_running():
            asyncio.run_coroutine_threadsafe(broadcast_log_async(log_entry), loop)

def getSubTaskList(inputTask="Say Hello"):
    logComputationToFile("Generating sub task list for the task: " + inputTask)
    chatHistoryString = "\n".join(str(item) for item in chatHistory)

    sysRole = """You are a function that takes one task as input. You only have access to a cli terminal with windows powershell commands.
    The definition of an atomic task is a task that can be run by a one-line shell command compatible with both Windows.
    If the inputted task can be broken down into modular subtasks, return a JSON with fields "atomic":"false" and "subtasks":"<list of subtasks>".
    If the inputted task is atomic, return a JSON with fields "atomic":"true" and "command":"<shell command>".
    Python is installed on the system. Use {python} <filename> to run Python scripts, where {python} is the Python executable.
    For file writing, use shell commands like echo or cat to create files.
    Always start a task by creating a directory using a shell command (mkdir <directory_name> on Linux, md <directory_name> on Windows).
    The following is the chat history: """ + chatHistoryString

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": sysRole},
            {"role": "user", "content": "The input task is :" + inputTask},
        ],
        stream=False
    )

    chatHistory.append({"inputTask": inputTask, "response": response.choices[0].message.content})
    logComputationToFile("Response from the API: " + response.choices[0].message.content)

    # Clean the response to extract valid JSON
    response_content = response.choices[0].message.content
    response_content = response_content.replace("```json", "").replace("```", "").replace("json", "").strip()
    try:
        jsonform = json.loads(response_content)
    except json.JSONDecodeError as e:
        logComputationToFile(f"JSON parsing error: {str(e)}")
        raise ValueError(f"Failed to parse API response as JSON: {response_content}")
    return jsonform

class Node:
    def __init__(self, task: str, level: int = 99999) -> None:
        self.task: str = task
        self.parent: bool = False
        self.leaf: bool = False
        self.level: int = level
        self.subTasks: List[Node] = []

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
        if response["atomic"] == "false":
            self.addListOfSubtasks(response["subtasks"])
            logComputationToFile("The task is not atomic, so we need to add the subtasks of the task: " + self.task)
            for childTask in self.subTasks:
                childTask.fillTreeWithTasks()
        if response["atomic"] == "true":
            self.leaf = True
            self.task = response["command"]

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

# HTTP Server to serve the log file, UI, and handle UI logs
PORT = 8000
class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_PUT(self):
        if self.path == '/task.txt':
            content_length = int(self.headers['Content-Length'])
            content = self.rfile.read(content_length).decode('utf-8')
            with open('task.txt', 'w', encoding='utf-8') as f:
                f.write(content)
            self.send_response(200)
            self.end_headers()
            logComputationToFile(f"Received task via PUT: {content}")
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/log-ui':
            content_length = int(self.headers['Content-Length'])
            content = self.rfile.read(content_length).decode('utf-8')
            with open('ui.log', 'a', encoding='utf-8') as f:
                f.write(content)
            self.send_response(200)
            self.end_headers()
            logComputationToFile(f"UI log received: {content.strip()}")
        else:
            self.send_response(404)
            self.end_headers()

# WebSocket server setup
connected_clients = set()
async def websocket_handler(websocket, path):
    logComputationToFile(f"New WebSocket connection on path: {path}")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            logComputationToFile(f"WebSocket message received: {message}")
            # Handle incoming messages if needed
    except Exception as e:
        logComputationToFile(f"WebSocket error: {str(e)}")
    finally:
        connected_clients.remove(websocket)
        logComputationToFile("WebSocket connection closed")

# Start the HTTP server in a separate thread
def start_http_server():
    try:
        with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
            print(f"Serving HTTP on port {PORT}")
            httpd.serve_forever()
    except Exception as e:
        logComputationToFile(f"HTTP server error: {str(e)}")

# Start the WebSocket server
async def start_websocket_server():
    async with websockets.serve(websocket_handler, "localhost", 8765):
        print("WebSocket server running on ws://localhost:8765")
        await asyncio.Future()  # Run forever

# Process task from task.txt
async def process_task(task):
    if task.strip():
        logComputationToFile(f"Processing new task: {task}")
        tree = NaryTree(root_task=task)
        tree.root.fillTreeWithTasks()
        stepsTaken = tree.postorder_traversal()
        print("Currently executing the tasks:")
        for step in stepsTaken:
            logComputationToFile("Executing the command: " + step)
            try:
                result = subprocess.run(step, shell=True, capture_output=True, text=True)
                shellexecutionresult = result.stdout or result.stderr
            except subprocess.SubprocessError as e:
                shellexecutionresult = f"Error executing command: {str(e)}"
            logComputationToFile("The result of the command: " + shellexecutionresult + " \n")
            terminalExecutionHistory.append({"command": step, "response": shellexecutionresult})

# Monitor task.txt for changes
async def monitor_task_file():
    logComputationToFile("Starting task.txt file monitoring")
    async for changes in watchfiles.awatch('task.txt'):
        for change in changes:
            if change[0] == watchfiles.Change.modified or change[0] == watchfiles.Change.added:
                try:
                    with open("task.txt", "r", encoding='utf-8') as file:
                        rootTask = file.read().strip()
                    logComputationToFile(f"Detected change in task.txt: {rootTask}")
                    await process_task(rootTask)
                except Exception as e:
                    logComputationToFile(f"Error reading task.txt: {str(e)}")

# Main execution
if __name__ == "__main__":
    # Create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Start HTTP server in a background thread
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()

    # Start WebSocket server and task monitoring
    tasks = [
        start_websocket_server(),
        monitor_task_file()
    ]
    try:
        # Initialize task.txt if it doesn't exist
        if not os.path.exists("task.txt"):
            logComputationToFile("Creating empty task.txt")
            with open("task.txt", "w", encoding='utf-8') as file:
                file.write("")
        # Run initial task if present
        with open("task.txt", "r", encoding='utf-8') as file:
            rootTask = file.read().strip()
        if rootTask:
            loop.run_until_complete(process_task(rootTask))
        # Run WebSocket server and file monitoring
        loop.run_until_complete(asyncio.gather(*tasks))
    except KeyboardInterrupt:
        logComputationToFile("Shutting down server")
        # Cancel all running tasks
        for task in asyncio.all_tasks(loop):
            task.cancel()
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        logComputationToFile("Event loop closed")