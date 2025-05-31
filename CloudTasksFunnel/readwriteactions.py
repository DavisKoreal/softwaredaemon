import subprocess

class EchoFileOperations:
    def writeToFile(self, filepath, content):
        """Writes content to a file using echo, overwriting existing content"""
        try:
            # Using > to overwrite file
            command = f"echo '{content}' > {filepath}"
            subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error writing to file {filepath}: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error writing to file {filepath}: {str(e)}")

    def appendToFile(self, filepath, content):
        """Appends content to a file using echo"""
        try:
            # Using >> to append to file
            command = f"echo '{content}' >> {filepath}"
            subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error appending to file {filepath}: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error appending to file {filepath}: {str(e)}")

    def readFromFile(self, filepath):
        """Reads content from a file (using cat since echo doesn't read)"""
        try:
            # Using cat to read file content since echo is for writing
            command = f"cat {filepath}"
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error reading from file {filepath}: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error reading from file {filepath}: {str(e)}")

    def checkFileExists(self, filepath):
        """Checks if a file exists using test command"""
        try:
            command = f"test -f {filepath} && echo 'true' || echo 'false'"
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            return result.stdout.strip() == "true"
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error checking file existence {filepath}: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error checking file existence {filepath}: {str(e)}")