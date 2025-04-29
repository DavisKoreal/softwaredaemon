import shellinteractions

# Please install OpenAI SDK first: `pip3 install openai`
# !pip3 install openai
# %pip install openai

from openai import OpenAI
import json
import time

client = OpenAI(api_key="sk-9157cd146a344095baf8e3ef6454117b", base_url="https://api.deepseek.com")
chatHistory = [{"inputTask": " ", "response": " "}]
terminalExecutionHistory = [{"icommand": " ", "response": " "}]
feedbackHistory = [{"human feedback":" "}]

def logComputationToFile(logMessage):
    # This function logs the message to the log file
    # It takes a log file name and a log message as input
    # and appends the message to the log file.
    with open("taskagent.log", 'a') as f:
        f.write(time.asctime() + " : " + logMessage + "\n")
        f.close()


def getSubTaskList(inputTask="Say Hello"):
    # This function generates a list of sub tasks for a given task
    # returns a list of tasks if task can be broken down
    # into subtasks, else returns an empty list.
    logComputationToFile("Generating sub task list for the task: " + inputTask)
    #convert the chatHIstory list to a string
    
    chatHistoryString = ""
    for i in range(len(chatHistory)):
        chatHistoryString += str(chatHistory[i]) + "\n" 
    
    feedbackHistoryString = ""
    for i in range(len(chatHistory)):
        feedbackHistoryString += str(chatHistory[i]) + "\n" 


    sysRole =  """You are a function that takes one task as input. You already have access to a linux terminal with basic commands.
    The definition of an atomic task as a task that can be run by a one line linux shell command on the terminal.
    If the inputted task can be broken down into a list of modular subtasks, return a json having the following fields "atomic":"false" and "subtasks":"<enter the list of subtasks of the inputted task>". This list should only have the names of subtasks of the inputted task. These names should be a brief description of the task. Break the input into modular tasks.
    If the inputted task is an atomic task, only return the json with the following fields "atomic":"true" and "command":"<enter the linux command to achieve it>".
    Python is already installed on the system. You can use it to run any python code. If a task needs you to install a software package, return a one line command that installs the package. Do not check if it is in the system or not. Just return the command to install it since it is an atomic task.
    When you have to write into a file, use the linux command "printf" to write into the file. Do not use any other command to write into a file.
    When trying to run a python file, use the command "python3 <filename>" to run the file. Do not use any other command to run the file.
    The following is the chat history: """ + chatHistoryString + " the following is the feedback history " + feedbackHistoryString

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
    # logComputationToFile("Parsed JSON: " + str(jsonform))
    return jsonform



class Node:
    def __init__(self, task:str, level = 99999):
        self.task = task
        self.parent = False
        self.leaf = False
        self.level = level
        self.humaninput = False
        # self.addSubTasks()
        self.subTasks = []  # List to store any number of subTasks, or in this case, sub tasks

    # def addSubTask(self, subTaskName:str):
    #     """Add a child node with the given task"""
    #     child_node = Node(subTaskName, level=(self.level + 1))
    #     self.subTasks.append(child_node)
    #     self.parent = True
    #     return child_node
    
    def addListOfSubtasks(self, listofsubtasks):
        logComputationToFile("I want to add the following subtasks of the task: " + self.task)
        print("I want to add the following subtasks of the task: " + self.task + "\n")
        if len(listofsubtasks) == 0:
            return
        for task in listofsubtasks:
            print(task + "\n")
            self.subTasks.append(Node(task, level=(self.level + 1)))
        print("Give direction on these tasks")
        humaninput = input()
        feedbackHistory.append({"human feedback": humaninput})
        self.parent=True

    def fillTreeWithTasks(self):
        # logComputationToFile("Filling tree w"/)
        # get response from deepseek
        response = getSubTaskList(self.task)
        
        if response["atomic"] == "false":
            self.addListOfSubtasks(response["subtasks"])
            logComputationToFile("The task is not atomic, so we need to add the subtasks of the task: " + self.task)
            for childTask in self.subTasks:
                childTask.fillTreeWithTasks()
        
        # if this is an atomic task, then the task is equal to the command line task
        if response["atomic"] == "true":
            self.leaf = True
            self.task = response["command"]


    def __str__(self):
        """String representation of the node"""
        return str(self.task)

class NaryTree:
    def __init__(self, root_task=None):
        self.root = Node(root_task) if root_task is not None else None

    # def preorder_traversal(self, node=None):
    #     """Pre-order traversal: root, then subTasks from left to right"""
    #     if node is None and self.root is None:
    #         return []
        
    #     if node is None:
    #         node = self.root
        
    #     result = [node.task]
    #     for child in node.subTasks:
    #         result.extend(self.preorder_traversal(child))
    #     return result

    # before visiting a parent node, we need to visit all its subTasks first
    def postorder_traversal(self, node=None):
        """Post-order traversal: subTasks from left to right, then root"""
        if node is None and self.root is None:
            return []
        
        if node is None:
            node = self.root
        
        result = []
        if node.parent == True:
            for child in node.subTasks:
                result.extend(self.postorder_traversal(child))
        
        if node.parent == False:
            result.append(node.task)

        return result


    # we need level order to visit all nodes and querry deepseek for subtasks of that node
    # we can use this to get subtasks of a task
    # we start with the main task, which is the root node, and the main goal of the whole operation
    # then we get the subtasks of the main task, which are the subTasks of the root node
    # then we get the subtasks of the level one subtasks, which are the subTasks of the subTasks of the root node
    # then we get subtasks of the level two subtasks, which are the subTasks of the subTasks of the subTasks of the root node
    # and so on as long as a node can be broken down into a task, or in another flavour, as long as a node has subTasks
    # def level_order_traversal(self):
    #     """Level-order traversal using a queue"""
    #     if not self.root:
    #         return []
        
    #     result = []
    #     queue = [self.root]
        
    #     while queue:
    #         current = queue.pop(0)  # Dequeue
    #         result.append(current.task)
    #         # Add all subTasks to the queue
    #         queue.extend(current.subTasks)
        
    #     return result


# Example usage
if __name__ == "__main__":
    # Create a tree of tasks
    rootTask = input("What is the task that you want to be computed? ")
    tree = NaryTree(root_task=rootTask)
    tree.root.fillTreeWithTasks()

    stepsTaken = tree.postorder_traversal()
    print("Currently executing the tasks:")
    for step in stepsTaken:
        logComputationToFile("Executing the command: " + step)
        shellexecutionresult = daemon.executeCommand(step)
        logComputationToFile("The result of the command: " + shellexecutionresult + " \n")
