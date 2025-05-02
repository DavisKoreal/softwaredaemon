# Please install OpenAI SDK first: `pip install openai`
from openai import OpenAI
import json
import time
import shellinteractions
from typing import List
import os
import sys

client = OpenAI(api_key="sk-9157cd146a344095baf8e3ef6454117b", base_url="https://api.deepseek.com")
chatHistory = [{"inputTask": " ", "response": " "}]
terminalExecutionHistory = [{"command": " ", "response": " "}]

def getdirectoryHistory():
    print("Getting the directory history")

# a function that takes in a number n and returns a string of n "\t" characters
def getTabsBasedOnLevel(n):
    return "\t" * n

def logComputationToFile(logMessage):
    # This function logs the message to the log file
    # It takes a log file name and a log message as input
    # and appends the message to the log file.
    print(time.asctime() + " : " + logMessage + "\n")
    with open("../taskagent.log", 'a') as f:
        f.write(time.asctime() + " : " + logMessage + "\n")

def getSubTaskList(inputTask="Say Hello"):
    # Generates a list of subtasks for a given task
    logComputationToFile("Generating sub task list for the task: " + inputTask)
    #convert the chatHIstory list to a string
    chatHistoryString = ""
    for i in range(len(chatHistory)):
        chatHistoryString += str(chatHistory[i]) + "\n" 

    sysRole =  """You are a function that takes one task as input. You already have access to a linux terminal with basic commands.
    The definition of an atomic task as a task that can be run by a one line linux shell command on the terminal.
    If the inputted task can be broken down into a list of modular subtasks, return a json having the following fields "atomic":"false" and "subtasks":"<enter the list of subtasks of the inputted task>". This list should only have the names of subtasks of the inputted task. These names should be a brief description of the task. Break the input into modular tasks.
    If the inputted task is an atomic task, only return the json with the following fields "atomic":"true" and "command":"<enter the linux command to achieve it>".
    If a task needs you to install a software package, return a one line command that installs the package. Do not check if it is in the system or not. Just return the command to install it since it is an atomic task. If it had not been installed before, it will be installed now. If it is already installed, it will be skipped/updated so both scenarios are taken care of.                        
    When trying to run a python file, use the command "python3 <filename>" to run the file. Do not use any other command to run the file.
    Always start a programming task by creating an appropriate directory to store the files. Use the command "mkdir <directory_name>" to create a directory.
    You are limited to linux commands as how you interface with the system.
    You have an empty repository to work with. Create a directory for the main task and then you can create files or folders inside that directory as need arises
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
    rootTask = input("What is the task that you want to be computed? ")
    tree = NaryTree(root_task=rootTask)
    daemon = shellinteractions.ShellInteractions()
    tree.root.fillTreeWithTasks()

    stepsTaken = tree.postorder_traversal()
    print("Currently executing the tasks:")
    for step in stepsTaken:
        logComputationToFile("Executing the command: " + step)
        shellexecutionresult = daemon.executeCommand(step)
        logComputationToFile("The result of the command: " + shellexecutionresult + " \n")
        terminalExecutionHistory.append({"command": step, "response": shellexecutionresult})
 
    print("All tasks have been executed successfully.")