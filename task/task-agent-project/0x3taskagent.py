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
import re
import logging
import aiofiles
import datetime
import uuid
import jsonschema

# Load environment variables from .env file
load_dotenv(dotenv_path=".env")

# Set the OpenAI API key and base URL
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    print("Error: DEEPSEEK_API_KEY not found in .env file")
    sys.exit(1)

# Get ports from env vars for configurability
HTTP_PORT = int(os.getenv("HTTP_PORT", 8000))
WS_PORT = int(os.getenv("WS_PORT", 8765))

# Setup logging with basicConfig
logging.basicConfig(
    filename='taskagent.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Define JSON schema for API response validation
SUBTASK_SCHEMA = {
    "type": "object",
    "properties": {
        "atomic": {"type": "string", "enum": ["true", "false"]},
    },
    "required": ["atomic"],
    "oneOf": [
        {
            "properties": {
                "atomic": {"const": "true"},
                "command": {"type": "string"}
            },
            "required": ["command"]
        },
        {
            "properties": {
                "atomic": {"const": "false"},
                "subtasks": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["subtasks"]
        }
    ]
}

class TaskAgent:
    def __init__(self):
        """Initialize the TaskAgent with global state encapsulated."""
        self.chat_history = [{"inputTask": " ", "response": " "}]
        self.terminal_history = [{"command": " ", "response": " "}]

        self.connected_clients = set()
        self.loop = asyncio.get_event_loop()
        self.client_rate_limits = {}
        self.client_ids = {}
        self.client_messages = {}
        self.rate_limit_window = 600  # seconds
        self.rate_limit_max = 100  # messages per window

        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        print("OpenAI client initialized")

    def get_directory_history(self):
        """Placeholder for getting directory history."""
        self.log("Getting the directory history")

    def log(self, message, level="info"):
        logging.log(getattr(logging, level.upper()), message)
        timestamp = datetime.datetime.now().isoformat()
        log_json = json.dumps({"timestamp": timestamp, "message": message, "level": level.lower()})
        print(f"[{timestamp}] [{level.upper()}] {message}")
        if self.connected_clients and self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.broadcast_log_async(log_json), self.loop)

    def log_error(self, message):
        self.log(message, level="error")

    def log_warning(self, message):
        self.log(message, level="warning")

    async def broadcast_log_async(self, log_json):
        if self.connected_clients:
            await asyncio.gather(*(client.send(log_json) for client in self.connected_clients))

    async def send_to_client(self, websocket, data):
        await websocket.send(json.dumps(data))

    def get_sub_task_list(self, input_task="Say Hello"):
        self.log(f"Generating sub task list for the task: {input_task}")
        chat_history_string = "\n".join(str(item) for item in self.chat_history)

        sys_role = """You are a function that takes one task as input. You only have access to a cli terminal with Windows cmd commands.
        The definition of an atomic task is a task that can be run by a one-line shell command compatible with Windows cmd.
        If the inputted task can be broken down into modular subtasks, return a JSON with fields "atomic":"false" and "subtasks":"<list of subtasks>".
        If the inputted task is atomic, return a JSON with fields "atomic":"true" and "command":"<shell command>".
        Python is installed on the system. Use python <filename> to run Python scripts, where python is the Python executable.
        For writing files with complex content like code, ALWAYS use python -c to execute a small script that writes the file, using triple single quotes for multiline strings to avoid escaping issues.
        Example for file writing: python -c "with open('file.cpp', 'w', encoding='utf-8') as f: f.write('''#include <iostream>\nint main() { return 0; }''')"
        Always start a task by creating a directory using a shell command (md <directory_name> on Windows).
        The following is the chat history: """ + chat_history_string

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": sys_role},
                    {"role": "user", "content": "The input task is :" + input_task},
                ],
                stream=False
            )
            response_content = response.choices[0].message.content
            self.log(f"Response from the API: {response_content}")
        except Exception as e:
            self.log_error(f"API call error: {str(e)}")
            raise

        self.chat_history.append({"inputTask": input_task, "response": response_content})

        response_content = response_content.replace("json", "").replace("```", "").replace("json", "").strip()
        json_match = re.search(r'\{[\s\S]*\}', response_content)
        if json_match:
            response_content = json_match.group(0)

        try:
            json_form = json.loads(response_content)
            jsonschema.validate(instance=json_form, schema=SUBTASK_SCHEMA)
        except json.JSONDecodeError as e:
            self.log_error(f"JSON parsing error: {str(e)}")
            raise ValueError(f"Failed to parse API response as JSON: {response_content}")
        except jsonschema.exceptions.ValidationError as e:
            self.log_error(f"JSON schema validation error: {str(e)}")
            raise ValueError(f"API response does not match expected schema: {response_content}")

        return json_form

class Node:
    def __init__(self, task: str, level: int = 99999) -> None:
        self.task: str = task
        self.parent: bool = False
        self.leaf: bool = False
        self.level: int = level
        self.sub_tasks: List['Node'] = []

    def add_sub_task(self, sub_task_name: str):
        child_node = Node(sub_task_name, level=(self.level + 1))
        self.sub_tasks.append(child_node)
        self.parent = True
        return child_node

    def add_list_of_subtasks(self, list_of_subtasks):
        if not list_of_subtasks:
            return
        for task in list_of_subtasks:
            self.sub_tasks.append(Node(task, level=(self.level + 1)))
        self.parent = True

    def fill_tree_with_tasks(self, agent: TaskAgent):
        response = agent.get_sub_task_list(self.task)
        if response["atomic"] == "false":
            self.add_list_of_subtasks(response["subtasks"])
            for child_task in self.sub_tasks:
                child_task.fill_tree_with_tasks(agent)
        if response["atomic"] == "true":
            self.leaf = True
            self.task = response["command"]

    def __str__(self):
        return str(self.task)

class NaryTree:
    def __init__(self, root_task=None, start_level=0):
        self.root = Node(root_task, level=start_level) if root_task is not None else None

    def postorder_traversal(self, node=None):
        if node is None and self.root is None:
            return []
        if node is None:
            node = self.root
        result = []
        if node.parent:
            for child in node.sub_tasks:
                result.extend(self.postorder_traversal(child))
        if not node.parent:
            result.append(node.task)
        return result

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, agent=None, **kwargs):
        self.agent = agent
        super().__init__(*args, **kwargs)

    def do_POST(self):
        request_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        self.agent.log(f"[{timestamp}] [Request {request_id}] POST request received on {self.path}")

        if self.path == '/log-ui':
            content_length = int(self.headers['Content-Length'])
            content = self.rfile.read(content_length).decode('utf-8')
            with open('ui.log', 'a', encoding='utf-8') as f:
                f.write(content)
            self.send_response(200)
            self.end_headers()
            response_timestamp = datetime.datetime.now().isoformat()
            self.agent.log(f"[{response_timestamp}] [Request {request_id}] UI log received: {content.strip()}")
        else:
            self.send_response(404)
            self.end_headers()
            response_timestamp = datetime.datetime.now().isoformat()
            self.agent.log(f"[{response_timestamp}] [Request {request_id}] 404 response sent")

class MyTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def start_http_server(agent):
    Handler = lambda *args, **kwargs: CustomHandler(*args, agent=agent, **kwargs)
    try:
        with MyTCPServer(("127.0.0.1", HTTP_PORT), Handler) as httpd:
            print(f"Serving HTTP on 127.0.0.1 port {HTTP_PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"HTTP server error: {str(e)}")

async def websocket_handler(websocket, path, agent: TaskAgent):
    client_id = str(uuid.uuid4())
    agent.client_ids[websocket] = client_id
    agent.client_messages[client_id] = []
    timestamp = datetime.datetime.now().isoformat()
    print(f"[{timestamp}] [Client {client_id}] New WebSocket connection on path: {path}")
    agent.connected_clients.add(websocket)

    try:
        async with aiofiles.open('taskagent.log', 'r', encoding='utf-8') as f:
            lines = await f.readlines()
        for line in lines:
            if line.strip():
                try:
                    timestamp_str, level, message = line.strip().split(' - ', 2)
                    log_json = json.dumps({"timestamp": timestamp_str, "message": message, "level": level.lower()})
                    await agent.send_to_client(websocket, json.loads(log_json))
                except ValueError:
                    print(f"Skipping malformed log line: {line.strip()}")
                    pass
    except Exception as e:
        print(f"[{timestamp}] [Client {client_id}] Error sending existing logs: {str(e)}")

    try:
        async for message in websocket:
            recv_timestamp = datetime.datetime.now().isoformat()
            print(f"[{recv_timestamp}] [Client {client_id}] Received: {message}")

            now = time.time()
            agent.client_messages[client_id] = [t for t in agent.client_messages[client_id] if now - t < agent.rate_limit_window]
            if len(agent.client_messages[client_id]) >= agent.rate_limit_max:
                error_data = {"error": "Rate limit exceeded"}
                await agent.send_to_client(websocket, error_data)
                continue
            agent.client_messages[client_id].append(now)

            try:
                data = json.loads(message)
                action = data.get('action')

                if action == 'submit_task':
                    task = data.get('task')
                    if task:
                        asyncio.create_task(agent.process_task(task))
                        response_data = {"response": "task_submitted", "task": task}
                        await agent.send_to_client(websocket, response_data)
                    else:
                        await agent.send_to_client(websocket, {"error": "Missing task field"})

                elif action == 'get_history':
                    hist_type = data.get('type')
                    if hist_type == 'chat':
                        response_data = {"response": "history", "type": "chat", "data": agent.chat_history}
                        await agent.send_to_client(websocket, response_data)
                    elif hist_type == 'terminal':
                        response_data = {"response": "history", "type": "terminal", "data": agent.terminal_history}
                        await agent.send_to_client(websocket, response_data)
                    else:
                        await agent.send_to_client(websocket, {"error": "Invalid history type"})
                else:
                    await agent.send_to_client(websocket, {"error": "Unknown action"})
            except json.JSONDecodeError:
                await agent.send_to_client(websocket, {"error": "Invalid JSON"})
            except Exception as e:
                print(f"Error handling message: {str(e)}")
                await agent.send_to_client(websocket, {"error": "Server error"})
    except Exception as e:
        print(f"[{timestamp}] [Client {client_id}] WebSocket error: {str(e)}")
    finally:
        agent.connected_clients.remove(websocket)
        client_id = agent.client_ids.pop(websocket, None)
        agent.client_messages.pop(client_id, None)
        timestamp = datetime.datetime.now().isoformat()
        print(f"[{timestamp}] [Client {client_id}] WebSocket connection closed")

async def start_websocket_server(agent, port=WS_PORT):
    while True:
        try:
            async with websockets.serve(
                lambda ws: websocket_handler(ws, "/", agent),  # fixed: only pass ws
                "127.0.0.1", port
            ):
                print(f"WebSocket server running on ws://127.0.0.1:{port}")
                await asyncio.Future()
        except OSError as e:
            if e.errno == 10048:
                print(f"Port {port} in use, trying {port+1}")
                port += 1
            else:
                raise

async def process_task(self, task):
    if task.strip():
        self.log(f"Processing new task: {task}")
        tree = NaryTree(root_task=task)
        tree.root.fill_tree_with_tasks(self)
        steps_taken = tree.postorder_traversal()
        self.log("Currently executing the tasks:")
        for step in steps_taken:
            self.log(f"Executing the command: {step}")
            try:
                result = subprocess.run(step, shell=True, capture_output=True, text=True)
                shell_execution_result = result.stdout or result.stderr
            except subprocess.SubprocessError as e:
                shell_execution_result = f"Error executing command: {str(e)}"
                self.log_error(shell_execution_result)
            self.log(f"The result of the command: {shell_execution_result}")
            self.terminal_history.append({"command": step, "response": shell_execution_result})

TaskAgent.process_task = process_task

if __name__ == "__main__":
    async def main():
        agent = TaskAgent()
        print("TaskAgent initialized")

        http_thread = threading.Thread(target=start_http_server, args=(agent,), daemon=True)
        http_thread.start()

        tasks = [start_websocket_server(agent)]
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("Shutting down server")
            for task in asyncio.all_tasks():
                task.cancel()
            await agent.loop.shutdown_asyncgens()
            agent.loop.close()
            print("Event loop closed")

    asyncio.run(main())
