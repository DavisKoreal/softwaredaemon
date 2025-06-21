import os
import subprocess
import platform
from collections import defaultdict

class ShellInteractions:

    def __init__(self):
        self.ActionsDictionary: defaultdict[str, callable] = defaultdict(lambda: self.unknown_action)
        self.ActionsDictionary.update({
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
            "runPythonScript": self.runPythonScript,
            "askForUserInput": self.askForUserInput,
            "seeFileContent": self.seeFileContent,
            "writeToFile": self.writeToFile
        })
        
    def getCurrentDirectory(self):
        """Returns the current working directory"""
        try:
            return os.getcwd()
        except Exception as e:
            raise Exception(f"Error getting current directory: {str(e)}")

    def changeDirectory(self, path):
        """Changes the current working directory to the specified path"""
        try:
            os.chdir(path)
            return True
        except Exception as e:
            raise Exception(f"Error changing directory: {str(e)}")

    def listDirectoryContents(self):
        """Returns a list of files and directories in the current directory"""
        try:
            return os.listdir()
        except Exception as e:
            raise Exception(f"Error listing directory contents: {str(e)}")

    def executeCommand(self, command):
        """Executes a shell command and returns its output"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, executable="/bin/bash")
            return result.stdout
        except subprocess.CalledProcessError as e:
            return e.stderr
        except Exception as e:
            raise Exception(f"Error executing command: {str(e)}")

    def getFileSize(self, filepath):
        """Returns the size of a file in bytes"""
        try:
            return os.path.getsize(filepath)
        except Exception as e:
            raise Exception(f"Error getting file size: {str(e)}")

    def checkFileExists(self, filepath):
        """Returns True if file exists, False otherwise"""
        try:
            return os.path.exists(filepath)
        except Exception as e:
            raise Exception(f"Error checking file existence: {str(e)}")

    def getEnvironmentVariable(self, var_name):
        """Returns the value of a specified environment variable"""
        try:
            return os.environ.get(var_name)
        except Exception as e:
            raise Exception(f"Error getting environment variable: {str(e)}")

    def createDirectory(self, dir_name):
        """Creates a new directory with the specified name"""
        try:
            os.makedirs(dir_name, exist_ok=True)
            return True
        except Exception as e:
            raise Exception(f"Error creating directory: {str(e)}")

    # def removeFile(self, filepath):
    #     """Removes the specified file"""
    #     try:
    #         os.remove(filepath)
    #         return True
    #     except Exception as e:
    #         raise Exception(f"Error removing file: {str(e)}")

    def getFileModificationTime(self, filepath):
        """Returns the last modification time of a file"""
        try:
            return os.path.getmtime(filepath)
        except Exception as e:
            raise Exception(f"Error getting file modification time: {str(e)}")
        
    def getNamesOfAllFilesAndDirectories(self):
        """Returns a list of all files and directories in the current directory"""
        try:
            return os.listdir()
        except Exception as e:
            raise Exception(f"Error getting names of files and directories: {str(e)}")
        
    def getSystemInfo(self):
        """Returns system information including OS name and version"""
        try:
            return {
                "os_name": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.architecture(),
                "machine": platform.machine(),
                "processor": platform.processor()
            }
        except Exception as e:
            raise Exception(f"Error getting system information: {str(e)}")
        
    def getCurrentUser(self):
        """Returns the current user name"""
        try:
            return os.getlogin()
        except Exception as e:
            raise Exception(f"Error getting current user: {str(e)}")
    
    def getPythonExecutable(self):
        """Returns the path to the Python executable"""
        try:
            return os.path.abspath(os.path.join(os.path.dirname(__file__), 'python'))
        except Exception as e:
            raise Exception(f"Error getting Python executable path: {str(e)}")
        
    def runPythonScript(self, script_path, *args):
        """Runs a Python script with the given arguments
        and returns its output.
        """
        try:
            command = f"{self.getPythonExecutable()} {script_path} {' '.join(args)}"
            result = subprocess.run(command, shell=True, capture_output=True, text=True, executable="/bin/bash")
            return result.stdout
        except subprocess.CalledProcessError as e:
            return e.stderr
        except Exception as e:
            raise Exception(f"Error running Python script: {str(e)}")
        
    def askForUserInput(self, prompt):
        """Asks the user for input and returns the input"""
        try:
            return input(prompt)
        except Exception as e:
            raise Exception(f"Error asking for input: {str(e)}")
        
    def seeFileContent(self, filepath):
        """Returns the content of a file as a string"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading file content: {str(e)}")
        
    def writeToFile(self, filepath, content):
        """Writes the specified content to a file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        except Exception as e:
            raise Exception(f"Error writing to file: {str(e)}")
        

def testShellInteractionsClassUsingActionsDictionary():
    shell_interactions = ShellInteractions()
    
    # Example usage of the ActionsDictionary
    try:
        current_directory = shell_interactions.ActionsDictionary["getCurrentDirectory"]()
        print(f"\n\nCurrent Directory: {current_directory}")
        
        # Change directory to a new path (example)
        shell_interactions.ActionsDictionary["changeDirectory"]("/tmp")
        
        # List contents of the current directory
        contents = shell_interactions.ActionsDictionary["listDirectoryContents"]()
        print(f"\n\nContents of Current Directory: {contents}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

class Agent:
    def __init__(self):
        self.shell_interactions = ShellInteractions()

    def perform_action(self, action_name, *args):
        """Performs an action based on the action name and arguments"""
        if action_name in self.shell_interactions.ActionsDictionary:
            return self.shell_interactions.ActionsDictionary[action_name](*args)
        else:
            raise ValueError(f"Unknown action: {action_name}")
        
    def getListOfActionsToPlan(self):
        """Returns a tree of actions that can be performed by the agent"""
        return list(self.shell_interactions.ActionsDictionary.keys())
        
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
    testShellInteractionsClassUsingActionsDictionary()
    testAgentClassUsingShellInteractions()
    