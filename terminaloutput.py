import subprocess
import threading
import queue
import sys

class TerminalOutputCapture:
    def __init__(self):
        """Initialize the output capture with a queue for storing output"""
        self.output_queue = queue.Queue()
        self.process = None
        self.running = False
        self.thread = None

    def startCapture(self, command):
        """Start capturing terminal output for the given command"""
        try:
            if self.running:
                raise Exception("Capture is already running")
            
            # Start the process with piped output
            self.process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            self.running = True
            
            # Start thread to read output
            self.thread = threading.Thread(target=self._read_output)
            self.thread.daemon = True
            self.thread.start()
            
            return True
        except Exception as e:
            raise Exception(f"Error starting capture: {str(e)}")

    def _read_output(self):
        """Internal method to read output from process and put it in queue"""
        try:
            while self.running and self.process:
                # Read stdout line by line
                stdout_line = self.process.stdout.readline()
                if stdout_line:
                    self.output_queue.put(("stdout", stdout_line.strip()))
                
                # Read stderr line by line
                stderr_line = self.process.stderr.readline()
                if stderr_line:
                    self.output_queue.put(("stderr", stderr_line.strip()))
                
                # Check if process has ended
                if self.process.poll() is not None:
                    self.running = False
                    break
                    
        except Exception as e:
            self.output_queue.put(("error", f"Error reading output: {str(e)}"))
        finally:
            self.running = False

    def getOutput(self, timeout=None):
        """Get the next available output from the queue"""
        try:
            if not self.running:
                raise Exception("Capture is not running")
                
            output = self.output_queue.get(timeout=timeout)
            return output  # Returns tuple (source, content)
        except queue.Empty:
            return None
        except Exception as e:
            raise Exception(f"Error getting output: {str(e)}")

    def stopCapture(self):
        """Stop capturing terminal output"""
        try:
            if not self.running:
                raise Exception("No capture is running")
                
            self.running = False
            if self.process:
                self.process.terminate()
                self.process.wait()
                self.process = None
            if self.thread:
                self.thread.join()
                self.thread = None
            return True
        except Exception as e:
            raise Exception(f"Error stopping capture: {str(e)}")

    def isRunning(self):
        """Check if capture is currently running"""
        try:
            return self.running
        except Exception as e:
            raise Exception(f"Error checking status: {str(e)}")
        
if __name__ == "__main__":
    capture = TerminalOutputCapture()
    command = "python3 test.py"
    
    try:
        if capture.startCapture(command):
            while capture.isRunning():
                output = capture.getOutput(timeout=1)
                if output:
                    source, content = output
                    print(f"[{source}] {content}")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        capture.stopCapture()