#!/usr/bin/env python3
"""
Trust Bench Studio Service Manager
Starts both the API server and job processor worker automatically.
"""

import asyncio
import multiprocessing
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import uvicorn


def setup_environment():
    """Set up the Python environment and paths."""
    project_root = Path(__file__).parent.absolute()
    os.environ["PYTHONPATH"] = str(project_root)
    os.chdir(project_root)
    return project_root


def run_job_processor():
    """Run the job processor in a separate process."""
    try:
        from job_processor_demo import process_pending_jobs
        print("🤖 Job Processor: Starting background worker...")
        asyncio.run(process_pending_jobs())
    except KeyboardInterrupt:
        print("🤖 Job Processor: Stopped by user")
    except Exception as e:
        print(f"🤖 Job Processor: Error - {e}")


def run_api_server(host: str = "127.0.0.1", port: int = 8001):
    """Run the FastAPI server."""
    try:
        print(f"🔌 API Server: Starting on http://{host}:{port}")
        uvicorn.run(
            "trust_bench_studio.api.server:app",
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("🔌 API Server: Stopped by user")
    except Exception as e:
        print(f"🔌 API Server: Error - {e}")


def main():
    """Main service manager."""
    setup_environment()
    
    print("🚀 Trust Bench Studio Service Manager")
    print("=====================================")
    print("Starting API server and job processor...")
    
    # Create processes for both services
    api_process = multiprocessing.Process(
        target=run_api_server,
        name="TrustBench-API"
    )
    
    job_process = multiprocessing.Process(
        target=run_job_processor,
        name="TrustBench-JobProcessor"
    )
    
    def cleanup_handler(signum, frame):
        print("\n🛑 Shutting down services...")
        if api_process.is_alive():
            api_process.terminate()
            api_process.join(timeout=5)
        if job_process.is_alive():
            job_process.terminate()
            job_process.join(timeout=5)
        print("✅ Cleanup complete")
        sys.exit(0)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup_handler)
    signal.signal(signal.SIGTERM, cleanup_handler)
    
    try:
        # Start both processes
        api_process.start()
        time.sleep(2)  # Let API server start first
        job_process.start()
        
        print("\n✅ Services started successfully!")
        print("🌐 Frontend: Open your browser and navigate to the UI")
        print("🔌 Backend API: http://127.0.0.1:8001")
        print("🤖 Job Processor: Running in background")
        print("\n📝 Repository analysis jobs will now complete automatically!")
        print("   - Submit a GitHub URL in the UI")
        print("   - Jobs will be processed in the background")
        print("   - Progress updates appear in real-time")
        print("\n⏹️  Press Ctrl+C to stop all services")
        
        # Keep main process alive and monitor children
        while api_process.is_alive() and job_process.is_alive():
            time.sleep(1)
            
        # If one process dies, clean up the other
        if not api_process.is_alive():
            print("❌ API server stopped unexpectedly")
        if not job_process.is_alive():
            print("❌ Job processor stopped unexpectedly")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cleanup_handler(None, None)


if __name__ == "__main__":
    main()