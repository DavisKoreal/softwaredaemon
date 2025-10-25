#!/usr/bin/env python3
"""
Test script to demonstrate the WebSocket server with sample data
"""
import json
import asyncio
import time
from websocketserver import WebSocketTaskServer, Node

def create_sample_tree():
    """Create a sample task tree with the new attributes"""
    # Root task
    root = Node("Create Simple HTML Website", 0)
    root.parent = True
    root.chatresponse = "Starting HTML website development project"
    
    # Level 1 tasks
    setup_task = Node("Setup Project Structure", 1)
    setup_task.parent = True
    setup_task.executionStarted = True
    setup_task.chatresponse = "Setting up basic project structure"
    
    # Level 2 tasks under Setup
    create_dir = Node("Create Project Directory", 2)
    create_dir.leaf = True
    create_dir.atomic = True
    create_dir.command = "mkdir website-project"
    create_dir.executionSuccess = True
    create_dir.chatresponse = "Directory created successfully"
    
    init_files = Node("Initialize HTML Files", 2)
    init_files.leaf = True
    init_files.atomic = True
    init_files.command = "touch index.html style.css script.js"
    init_files.executionStarted = True
    init_files.human_needed = True
    init_files.human_instructions = [
        "Verify all files are created in the correct directory",
        "Check file permissions are correct"
    ]
    
    setup_task.subTasks = [create_dir, init_files]
    
    # Level 1 - Development task
    develop_task = Node("Develop Website Content", 1)
    develop_task.parent = True
    develop_task.subtasks = [
        "Create HTML structure",
        "Add CSS styling", 
        "Implement contact form",
        "Add JavaScript validation"
    ]
    
    # Level 2 tasks under Development
    html_task = Node("Create HTML Structure", 2)
    html_task.leaf = True
    html_task.atomic = True
    html_task.command = "echo '<!DOCTYPE html><html><head><title>Contact Us</title></head><body><h1>Contact Form</h1></body></html>' > index.html"
    
    css_task = Node("Add CSS Styling", 2)
    css_task.leaf = True
    css_task.atomic = True
    css_task.command = "echo 'body { font-family: Arial; margin: 40px; } form { max-width: 400px; }' > style.css"
    
    form_task = Node("Implement Contact Form", 2)
    form_task.leaf = True
    form_task.atomic = True
    form_task.command = "echo 'function validateForm() { return true; }' > script.js"
    form_task.human_needed = True
    form_task.human_instructions = [
        "Test the form validation works correctly",
        "Verify form submission handles errors gracefully"
    ]
    
    develop_task.subTasks = [html_task, css_task, form_task]
    
    # Level 1 - Testing task
    test_task = Node("Test Website", 1)
    test_task.leaf = True
    test_task.atomic = True
    test_task.command = "python -m http.server 8080"
    test_task.chatresponse = "Ready to start local server for testing"
    test_task.human_needed = True
    test_task.human_instructions = [
        "Open browser and navigate to http://localhost:8080",
        "Test the contact form functionality",
        "Verify responsive design on different screen sizes"
    ]
    
    root.subTasks = [setup_task, develop_task, test_task]
    return root

async def simulate_task_execution(server, root):
    """Simulate task execution with status updates"""
    print("Starting task execution simulation...")
    
    # Wait a bit then start executing tasks
    await asyncio.sleep(3)
    
    # Find and execute tasks in order
    tasks_to_execute = [
        ("Create Project Directory", True, True),
        ("Initialize HTML Files", True, False), 
        ("Create HTML Structure", True, False),
        ("Add CSS Styling", True, True),
        ("Implement Contact Form", True, False),
        ("Test Website", True, False)
    ]
    
    for task_name, start, complete in tasks_to_execute:
        node = root.findNodeByTask(task_name)
        if node:
            print(f"Executing: {task_name}")
            node.executionStarted = start
            await server.broadcast_tree()
            await asyncio.sleep(2)  # Simulate work time
            
            if complete:
                node.executionSuccess = True
                node.chatresponse = f"Task '{task_name}' completed successfully"
                await server.broadcast_tree()
                print(f"Completed: {task_name}")
            else:
                print(f"Task '{task_name}' requires human intervention")
            
            await asyncio.sleep(1)
    
    print("Task execution simulation completed!")

async def main():
    """Main function to run the WebSocket server with sample data"""
    print("Creating WebSocket server...")
    server = WebSocketTaskServer("localhost", 8000)
    
    print("Creating sample task tree...")
    root = create_sample_tree()
    server.set_tree_root(root)
    
    print("Starting server and simulation...")
    # Start the server
    server_task = asyncio.create_task(server.start_server())
    
    # Start the simulation after a delay
    simulation_task = asyncio.create_task(simulate_task_execution(server, root))
    
    # Wait for both tasks
    await asyncio.gather(server_task, simulation_task, return_exceptions=True)

if __name__ == "__main__":
    print("WebSocket Task Tree Server Test")
    print("================================")
    print("This will start a WebSocket server on ws://localhost:8000")
    print("Connect your frontend to see the task tree visualization")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")