"""
Script to run the MCP server for data gathering
"""
import logging
import subprocess
import os
import time
from multiprocessing import Process

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def run_mcp_server():
    """Run the MCP server for data gathering"""
    logger.info("Starting MCP Server...")
    server_cmd = ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    
    try:
        # Change directory to the MCP server folder
        os.chdir("services/mcp-server")
        # Start the server process
        mcp_server = subprocess.Popen(
            server_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Log the server output
        logger.info("MCP Server started with PID: %s", mcp_server.pid)
        
        # Print the server output
        while True:
            output = mcp_server.stdout.readline()
            if not output and mcp_server.poll() is not None:
                break
            if output:
                print(f"MCP-SERVER: {output.strip()}")
                
        # Log if server exits
        if mcp_server.poll() is not None:
            logger.warning("MCP Server exited with code: %s", mcp_server.returncode)
    
    except Exception as e:
        logger.error("Error starting MCP Server: %s", str(e))
    finally:
        # Change back to the root directory
        os.chdir("../..")

if __name__ == "__main__":
    # Run in a separate process to avoid blocking the main thread
    server_process = Process(target=run_mcp_server)
    server_process.daemon = True
    server_process.start()
    
    # Keep the script running
    try:
        logger.info("MCP Server runner is active. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        server_process.terminate()