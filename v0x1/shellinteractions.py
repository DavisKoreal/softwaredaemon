import os
import subprocess
import platform
from collections import defaultdict

import os
import subprocess
import platform
import shutil
import getpass
import sys
from collections import defaultdict

class ShellInteractions:

    def __init__(self):
        self.Actions: defaultdict[str, callable] = defaultdict(lambda: self.unknown_action)
        self.Actions.update({
            "getCurrentDirectory": self.getCurrentDirectory,
            "changeDirectory": self.changeDirectory,
            "listDirectoryContents": self.listDirectoryContents,
            "executeCommand": self.executeCommand,
            "getFileSize": self.getFileSize,
            "checkFileExists": self.checkFileExists,
            "getEnvironmentVariable": self.getEnvironmentVariable,
            "createDirectory": self.createDirectory,
            # "removeFile": self.removeFile,  # Uncomment if needed
            "getFileModificationTime": self.getFileModificationTime,
            "getNamesOfAllFilesAndDirectories": self.getNamesOfAllFilesAndDirectories,
            "getSystemInfo": self.getSystemInfo,
            "getCurrentUser": self.getCurrentUser,
            "getPythonExecutable": self.getPythonExecutable,
            "getThisPythonExecutable": self.getThisPythonExecutable,
            "runPythonScript": self.runPythonScript,
            "askForUserInput": self.askForUserInput,
            "seeFileContent": self.seeFileContent,
            "writeToFile": self.writeToFile
        })

    def unknown_action(self):
        """Called when an unknown action is requested."""
        raise ValueError("Unknown action.")

    def getCurrentDirectory(self):
        """Returns the current working directory."""
        try:
            return os.getcwd()
        except Exception as e:
            raise Exception(f"Error getting current directory: {str(e)}")

    def changeDirectory(self, path):
        """Changes the current working directory to the specified path."""
        try:
            os.chdir(path)
            return True
        except Exception as e:
            raise Exception(f"Error changing directory: {str(e)}")

    def listDirectoryContents(self):
        """Returns a list of files and directories in the current directory."""
        try:
            return os.listdir()
        except Exception as e:
            raise Exception(f"Error listing directory contents: {str(e)}")

    def executeCommand(self, command):
        """
        Executes a shell command and returns its output.
        The command should be provided as a list of arguments, not a single string.
        """
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return e.stderr
        except Exception as e:
            raise Exception(f"Error executing command: {str(e)}")

    def getFileSize(self, filepath):
        """Returns the size of a file in bytes."""
        try:
            return os.path.getsize(filepath)
        except Exception as e:
            raise Exception(f"Error getting file size: {str(e)}")

    def checkFileExists(self, filepath):
        """Returns True if file exists, False otherwise."""
        try:
            return os.path.exists(filepath)
        except Exception as e:
            raise Exception(f"Error checking file existence: {str(e)}")

    def getEnvironmentVariable(self, var_name):
        """Returns the value of a specified environment variable."""
        try:
            return os.environ.get(var_name)
        except Exception as e:
            raise Exception(f"Error getting environment variable: {str(e)}")

    def createDirectory(self, dir_name):
        """Creates a new directory with the specified name."""
        try:
            os.makedirs(dir_name, exist_ok=True)
            return True
        except Exception as e:
            raise Exception(f"Error creating directory: {str(e)}")

    # def removeFile(self, filepath):
    #     """Removes the specified file."""
    #     try:
    #         os.remove(filepath)
    #         return True
    #     except Exception as e:
    #         raise Exception(f"Error removing file: {str(e)}")

    def getFileModificationTime(self, filepath):
        """Returns the last modification time of a file."""
        try:
            return os.path.getmtime(filepath)
        except Exception as e:
            raise Exception(f"Error getting file modification time: {str(e)}")
        
    def getNamesOfAllFilesAndDirectories(self):
        """Returns a list of all files and directories in the current directory."""
        return self.listDirectoryContents()
        
    def getSystemInfo(self):
        """Returns system information including OS name and version."""
        try:
            return {
                "os_name": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.architecture(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "release": platform.release()
            }
        except Exception as e:
            raise Exception(f"Error getting system information: {str(e)}")
        
    def getCurrentUser(self):
        """Returns the current user name."""
        try:
            # getpass.getuser() is more robust and cross-platform than os.getlogin()
            return getpass.getuser()
        except Exception as e:
            raise Exception(f"Error getting current user: {str(e)}")
    
    def getPythonExecutable(self):
        """Returns the path to the Python executable using shutil.which()."""
        try:
            # shutil.which() is a reliable cross-platform way to find executables
            python_exec = shutil.which("python") or shutil.which("python3")
            if python_exec:
                return python_exec
            raise FileNotFoundError("Could not find a Python executable.")
        except Exception as e:
            raise Exception(f"Error getting Python executable path: {str(e)}")

    def getThisPythonExecutable(self):
        """
        Returns the path to the Python executable running the script.
        This is the most reliable method for running other scripts with the same interpreter.
        """
        return sys.executable
    
    def runPythonScript(self, script_path, *args):
        """
        Runs a Python script with the given arguments and returns its output.
        The `getThisPythonExecutable()` method is used for maximum reliability.
        """
        try:
            python_executable = self.getThisPythonExecutable()
            command = [python_executable, script_path] + list(args)
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return e.stderr
        except Exception as e:
            raise Exception(f"Error running Python script: {str(e)}")
        
    def askForUserInput(self, prompt):
        """Asks the user for input and returns the input."""
        try:
            return input(prompt)
        except Exception as e:
            raise Exception(f"Error asking for input: {str(e)}")
        
    def seeFileContent(self, filepath):
        """Returns the content of a file as a string."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading file content: {str(e)}")
        
    def writeToFile(self, filepath, content):
        """Writes the specified content to a file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        except Exception as e:
            raise Exception(f"Error writing to file: {str(e)}")
        
    async def getResponse(inputTask="Say Hello"):

        from dotenv import load_dotenv
        from openai import OpenAI
        import json
        load_dotenv()
        DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

        sysRole:str =  """You are a function that takes one task as input. You already have access to a linux terminal with basic commands.
        The definition of an atomic task as a task that can be run by a one line linux shell command on the terminal.
        If the inputted task can be broken down into a list of modular subtasks, return a json having the following fields "atomic":"false" and "subtasks":"<enter the list of subtasks of the inputted task>". This list should only have the names of subtasks of the inputted task. These names should be a brief description of the task. Break the input into modular tasks.
        If the inputted task is an atomic task, only return the json with the following fields "atomic":"true" and "command":"<enter the linux command to achieve it>".
        Python is already installed on the system. You can use it to run any python code. If a task needs you to install a software package, return a one line command that installs the package. Do not check if it is in the system or not. Just return the command to install it since it is an atomic task.
        When you have to write into a file, use the linux command "printf" to write into the file. Do not use any other command to write into a file.
        When trying to run a python file, use the command "python3 <filename>" to run the file. Do not use any other command to run the file.
        The following is the chat history: """

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": sysRole},
                {"role": "user", "content": "The input task is :" + inputTask},
            ],
            stream=False
        )

        jsonform = json.loads(response.choices[0].message.content.replace("```json", "").replace("```", ""))
        # logComputationToFile("Parsed JSON: " + str(jsonform))
        return jsonform




def testShellInteractionsClassUsingActions():
    shell_interactions = ShellInteractions()
    
    # Example usage of the Actions
    try:
        current_directory = shell_interactions.Actions["getCurrentDirectory"]()
        print(f"\n\nCurrent Directory: {current_directory}")
        
        # Change directory to a new path (example)
        shell_interactions.Actions["changeDirectory"]("/tmp")
        
        # List contents of the current directory
        contents = shell_interactions.Actions["listDirectoryContents"]()
        print(f"\n\nContents of Current Directory: {contents}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

class Agent:
    def __init__(self):
        self.shell_interactions = ShellInteractions()

    def perform_action(self, action_name, *args):
        """Performs an action based on the action name and arguments"""
        if action_name in self.shell_interactions.Actions:
            return self.shell_interactions.Actions[action_name](*args)
        else:
            raise ValueError(f"Unknown action: {action_name}")
        
    def getListOfActionsToPlan(self):
        """Returns a tree of actions that can be performed by the agent"""
        return list(self.shell_interactions.Actions.keys())
        
def testAgentClassUsingShellInteractions():
    agent = Agent()
    
    # Example usage of the agent class
    try:
        current_directory = agent.perform_action("getCurrentDirectory")
        print(f"\n\n\nTESTING AGENT################\n\nCurrent Directory: {current_directory}")
        
        # Change directory to a new path (example)
        agent.perform_action("changeDirectory", "/tmp")
        
        # List contents of the current directory
        contents = agent.perform_action("listDirectoryContents")
        print(f"\n\nContents of Current Directory: {contents}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    testShellInteractionsClassUsingActions()
    testAgentClassUsingShellInteractions()
    