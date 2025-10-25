#!/usr/bin/env python3
"""
Quick verification script to test WebSocket connection
"""
import asyncio
import websockets
import json

async def test_websocket_connection():
    uri = "ws://localhost:8000"
    try:
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✓ Connected successfully!")
            
            # Wait for initial message
            message = await websocket.recv()
            data = json.loads(message)
            
            print("✓ Received initial data:")
            print(f"  Root task: {data['task']}")
            print(f"  Subtasks: {len(data.get('subTasks', []))}")
            
            # Check for new attributes
            if 'atomic' in data:
                print(f"  Atomic: {data.get('atomic')}")
            if 'chatresponse' in data:
                print(f"  Chat response: {data.get('chatresponse')}")
            if 'human_needed' in data:
                print(f"  Human needed: {data.get('human_needed')}")
                
            print("✓ WebSocket integration working correctly!")
            
    except Exception as e:
        print(f"✗ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_connection())