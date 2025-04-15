# main.py
from readwriteactions import EchoFileOperations
from shellinteractions import ShellInteractions
from terminaloutput import TerminalOutputCapture
import time
import os

def test_echo_file_operations():
    print("\n--- Testing EchoFileOperations ---")
    filepath = "testfile.txt"
    content1 = "Hello, world!"
    content2 = "Another line."

    echo = EchoFileOperations()

    print("Writing to file...")
    echo.writeToFile(filepath, content1)

    print("Appending to file...")
    echo.appendToFile(filepath, content2)

    print("Reading file contents:")
    print(echo.readFromFile(filepath))

    print("Checking file exists:")
    print("Exists?" , echo.checkFileExists(filepath))

def test_shell_interactions():
    print("\n--- Testing ShellInteractions ---")
    shell = ShellInteractions()
    test_dir = "testdir"

    print("Current directory:")
    print(shell.getCurrentDirectory())

    print("Creating a new directory:", test_dir)
    shell.createDirectory(test_dir)

    print("Changing to new directory...")
    shell.changeDirectory(test_dir)

    print("Listing contents (should be empty):")
    print(shell.listDirectoryContents())

    print("Environment variable PATH:")
    print(shell.getEnvironmentVariable("PATH"))

    # Go back to parent directory
    shell.changeDirectory("..")

    # Create test file for file size and mod time
    with open("testfile.txt", "w") as f:
        f.write("Hello again.")

    print("File size of testfile.txt:")
    print(shell.getFileSize("testfile.txt"))

    print("File modification time of testfile.txt:")
    print(shell.getFileModificationTime("testfile.txt"))

    print("Removing testfile.txt...")
    # shell.removeFile("testfile.txt")

def test_terminal_output_capture():
    print("\n--- Testing TerminalOutputCapture ---")
    capture = TerminalOutputCapture()
    command = "echo 'Captured output line 1' && echo 'Captured output line 2'"

    try:
        print("Starting capture...")
        capture.startCapture(command)

        while capture.isRunning():
            output = capture.getOutput(timeout=1)
            if output:
                source, content = output
                print(f"[{source}] {content}")
            else:
                break

        time.sleep(1)  # Give the thread a moment
    except Exception as e:
        print(f"Error during capture: {e}")
    finally:
        capture.stopCapture()

if __name__ == "__main__":
    test_echo_file_operations()
    test_shell_interactions()
    test_terminal_output_capture()
