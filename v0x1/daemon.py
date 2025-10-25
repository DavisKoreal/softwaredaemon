# Please install OpenAI SDK first: `pip install openai`
from openai import OpenAI
import json
import time
import shellinteractions
from typing import List
import os
import sys
from dotenv import load_dotenv
from systemPrompt import sysRole
# import SQLite for database operations below
import sqlite3




# We need a database class to store the chat history and terminal execution history and the tasks tree Nary tree
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


# Load environment variables from .env file
load_dotenv()
# Set the OpenAI API key and base URL
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  
print("The API key is: " + DEEPSEEK_API_KEY)

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
database = Database()

chatHistory = [{"inputTask": " ", "response": " "}]
terminalExecutionHistory = [{"command": " ", "response": " "}]

def getdirectoryHistory():
    print("Getting the directory history")

# a function that takes in a number n and returns a string of n "\t" characters
def getTabsBasedOnLevel(n):
    return "\t" * n

def logComputationToFile(logMessage):
    # Logs the message to the log file by appending
    log_file = os.path.join("taskagent.log")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(time.asctime() + " : " + logMessage + "\n")

def getSubTaskList(inputTask="Say Hello"):
    # Generates a list of subtasks for a given task
    logComputationToFile("Generating sub task list for the task: " + inputTask)
    chatHistoryString = "\n".join(str(item) for item in chatHistory)

    sysRole = sysRole + """ and the following is the chat history """+chatHistoryString

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
    jsonform = json.loads(response.choices[0].message.content.replace("```json", "").replace("```", ""))
    return jsonform

class Node:
    def __init__(self, task: str, level: int = 99999) -> None:
        self.task: str = task
        self.parent: bool = False
        self.leaf: bool = False
        self.level: int = level
        self.subTasks: List[Node] = []

    def addSubTask(self, subTaskName: str):
        """Add a child node with the given task"""
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
        """Post-order traversal: subTasks from left to right, then root"""
        if node is None and self.root is None:
            return []

        if node is None:
            node = self.root

        result = []
        if node.parent:
            logComputationToFile(getTabsBasedOnLevel(node.level)+"PARENT TASK: " + str(node.task))
            for child in node.subTasks:
                logComputationToFile(getTabsBasedOnLevel(child.level)+"The task of the child node: " + str(child.task))
                result.extend(self.postorder_traversal(child))

        if not node.parent:
            logComputationToFile(getTabsBasedOnLevel(node.level)+"LEAF TASK: " + str(node.task))
            result.append(node.task)

        return result

if __name__ == "__main__":
    # read from a local file called task.txt
    with open("task.txt", "r") as file:
        rootTask = file.read().strip()
    
    # output the number of characters in rootTask
    print("The task is: " + rootTask)

    
    # rootTask = input("What is the task that you want to be computed? ")
    tree = NaryTree(root_task=rootTask)
    daemon = shellinteractions.ShellInteractions()
    tree.root.fillTreeWithTasks()

    stepsTaken = tree.postorder_traversal()
    print("Currently executing the tasks:")

    # This loop should be replaced with a more reactive piece of code 
    # This just ensures that development is made as fast as possible
    for step in stepsTaken:
        logComputationToFile("Executing the command: " + step)
        shellexecutionresult = daemon.executeCommand(step)
        logComputationToFile("The result of the command: " + shellexecutionresult + " \n")
        terminalExecutionHistory.append({"command": step, "response": shellexecutionresult})
