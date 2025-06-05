#!/usr/bin/env python3
"""
Monitor deployment status by checking if orchestration is working
"""

import asyncio
import httpx
import time
from datetime import datetime


async def check_orchestration():
    """Check if orchestration is working"""
    url = "https://ultrai-core.onrender.com/api/orchestrator/feather"
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.post(
                url,
                json={"prompt": "Hi", "pattern": "gut"}
            )
            return response.status_code == 200
        except:
            return False


async def monitor():
    """Monitor deployment"""
    print("🔍 Monitoring UltraAI deployment...")
    print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")
    print("Checking every 30 seconds...\n")
    
    while True:
        working = await check_orchestration()
        status = "✅ WORKING" if working else "⏳ Not yet..."
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Orchestration: {status}")
        
        if working:
            print("\n🎉 Deployment successful! Orchestration is working!")
            break
            
        await asyncio.sleep(30)


if __name__ == "__main__":
    try:
        asyncio.run(monitor())
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")