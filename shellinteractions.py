import os
import subprocess

class ShellInteractions:
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
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout
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
            os.mkdir(dir_name)
            return True
        except Exception as e:
            raise Exception(f"Error creating directory: {str(e)}")

    def removeFile(self, filepath):
        """Removes the specified file"""
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            raise Exception(f"Error removing file: {str(e)}")

    def getFileModificationTime(self, filepath):
        """Returns the last modification time of a file"""
        try:
            return os.path.getmtime(filepath)
        except Exception as e:
            raise Exception(f"Error getting file modification time: {str(e)}")