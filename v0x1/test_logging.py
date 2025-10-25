#!/usr/bin/env python3
"""
Test logging configuration and demonstrate log output
"""
import sys
import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import time

def setup_test_logging():
    """Setup logging for testing (copy of the main setup)"""
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # File handlers
    file_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'daemon.log'),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'daemon_errors.log'),
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    # Create specialized loggers
    websocket_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'websocket.log'),
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    websocket_handler.setLevel(logging.DEBUG)
    websocket_handler.setFormatter(detailed_formatter)
    
    ws_logger = logging.getLogger('websocket')
    ws_logger.addHandler(websocket_handler)
    ws_logger.setLevel(logging.DEBUG)
    
    task_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'task_processing.log'),
        when='midnight',
        interval=1,
        backupCount=14,
        encoding='utf-8'
    )
    task_handler.setLevel(logging.DEBUG)
    task_handler.setFormatter(detailed_formatter)
    
    task_logger = logging.getLogger('task_processing')
    task_logger.addHandler(task_handler)
    task_logger.setLevel(logging.DEBUG)
    
    return logger, ws_logger, task_logger

# Initialize logging
logger, websocket_logger, task_logger = setup_test_logging()

def test_logging():
    """Test all logging levels and destinations"""
    print("Testing logging configuration...")
    print("Check the logs/ directory for output files")
    print()
    
    # Test main logger
    logger.debug("This is a DEBUG message - detailed diagnostic info")
    logger.info("This is an INFO message - general application flow")
    logger.warning("This is a WARNING message - something unusual happened")
    logger.error("This is an ERROR message - something failed")
    
    # Test WebSocket logger
    websocket_logger.info("WebSocket client connected from 192.168.1.100")
    websocket_logger.debug("Broadcasting tree data to 3 clients")
    websocket_logger.error("WebSocket connection failed: Connection refused")
    
    # Test task processing logger
    task_logger.info("Starting task decomposition for: Create HTML website")
    task_logger.debug("API response received: {'atomic': 'false', 'subtasks': [...]}")
    task_logger.info("Task breakdown completed - 5 subtasks created")
    
    print("✓ Log messages sent to all configured destinations")
    print()
    
    # Show log file locations
    log_dir = "logs"
    if os.path.exists(log_dir):
        print("Log files created:")
        for filename in os.listdir(log_dir):
            filepath = os.path.join(log_dir, filename)
            size = os.path.getsize(filepath)
            print(f"  {filename} ({size} bytes)")
    else:
        print("❌ logs/ directory not found")

def simulate_production_scenario():
    """Simulate a real production scenario with various log events"""
    print("\nSimulating production scenario...")
    
    # Simulate startup
    logger.info("Task Agent Daemon starting up")
    websocket_logger.info("WebSocket server starting on port 8000")
    
    time.sleep(0.1)
    
    # Simulate client connections
    for i in range(3):
        websocket_logger.info(f"Client {i+1} connected from 192.168.1.{100+i}")
        websocket_logger.debug(f"Sent initial tree data to client {i+1}")
    
    # Simulate task processing
    tasks = [
        "Create project directory",
        "Initialize git repository", 
        "Setup development environment",
        "Write application code",
        "Run tests"
    ]
    
    for i, task in enumerate(tasks, 1):
        task_logger.info(f"Processing task {i}/5: {task}")
        task_logger.debug(f"Calling AI API for task decomposition")
        
        # Simulate some processing time
        time.sleep(0.1)
        
        if i == 3:  # Simulate an error on task 3
            task_logger.error(f"Failed to execute task: {task} - Command not found")
            logger.error("Task execution failed, attempting recovery")
        else:
            task_logger.info(f"Task completed successfully: {task}")
            websocket_logger.debug(f"Broadcasting task completion to all clients")
    
    # Simulate client disconnections
    websocket_logger.info("Client disconnected normally")
    websocket_logger.warning("Client disconnected unexpectedly: Connection reset")
    
    logger.info("Production scenario simulation completed")
    print("✓ Production scenario logged")

if __name__ == "__main__":
    print("Task Agent Logging Test")
    print("=" * 30)
    
    # Test basic logging
    test_logging()
    
    # Simulate production scenario
    simulate_production_scenario()
    
    print("\nTo view logs in real-time, use:")
    print("  tail -f logs/daemon.log")
    print("  tail -f logs/websocket.log") 
    print("  tail -f logs/task_processing.log")
    print("  tail -f logs/daemon_errors.log")