# Please install OpenAI SDK first: `pip install openai`
from openai import OpenAI
import json
import time
import shellinteractions
from typing import List
import os
import sys
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
# Set the OpenAI API key and base URL
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  
print("The API key is: " + DEEPSEEK_API_KEY)

# client = OpenAI(api_key="sk-9157cd146a344095baf8e3ef6454117b", base_url="https://api.deepseek.com")
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

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

    sysRole = """You are a function that takes one task as input. You only have access to a cli terminal with basic linux commands.
    The definition of an atomic task is a task that can be run by a one-line shell command compatible with both Windows and Linux.
    If the inputted task can be broken down into modular subtasks, return a JSON with fields "atomic":"false" and "subtasks":"<list of subtasks>".
    If the inputted task is atomic, return a JSON with fields "atomic":"true" and "command":"<shell command>".
    Python is installed on the system. Use `{python} <filename>` to run Python scripts, where `{python}` is the Python executable.
    For file writing, use shell commands like `echo` or `cat` to create files. For example, to create a file named "test.txt" with the content "Hello World", use: echo "Hello World" > test.txt.
    Always start a task by creating a directory using a shell command (`mkdir <directory_name>` on Linux, `md <directory_name>` on Windows).
    The following is the chat history: """ + chatHistoryString

    # Replace {python} with the actual Python executable
    # sysRole = sysRole.format(python=sys.executable)

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
    taskstree = NaryTree(root_task=rootTask)
    daemon = shellinteractions.ShellInteractions()
    taskstree.root.fillTreeWithTasks()

    stepsTaken = taskstree.postorder_traversal()
    print("Currently executing the tasks:")

    # This loop should be replaced with a more reactive piece of code 
    # This just ensures that development is made as fast as possible
    for step in stepsTaken:
        logComputationToFile("Executing the command: " + step)
        shellexecutionresult = daemon.executeCommand(step)
        logComputationToFile("The result of the command: " + shellexecutionresult + " \n")
        terminalExecutionHistory.append({"command": step, "response": shellexecutionresult})