#!/usr/bin/env python3
"""
Script to start the Nova Sonic WebSocket server
"""

import os
import sys
import asyncio
from websocket_server import main

if __name__ == "__main__":
    # Set default environment variables
    os.environ.setdefault("HOST", "localhost")
    os.environ.setdefault("WS_PORT", "8081")
    os.environ.setdefault("HEALTH_PORT", "80")
    os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
    
    # Check for required AWS credentials
    if not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("AWS_SECRET_ACCESS_KEY"):
        print("❌ Error: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables are required")
        print("Please set your AWS credentials and try again")
        sys.exit(1)
    
    print("🚀 Starting Nova Sonic WebSocket Server...")
    print(f"📍 Host: {os.getenv('HOST')}")
    print(f"🔌 Port: {os.getenv('WS_PORT')}")
    print(f"🌍 Region: {os.getenv('AWS_DEFAULT_REGION')}")
    
    try:
        asyncio.run(main(
            host=os.getenv("HOST"),
            port=int(os.getenv("WS_PORT")),
            health_port=int(os.getenv("HEALTH_PORT"))
        ))
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1) 