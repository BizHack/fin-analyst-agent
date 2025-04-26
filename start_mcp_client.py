"""
Script to run the MCP client for data processing
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

def run_mcp_client():
    """Run the MCP client for data processing"""
    logger.info("Starting MCP Client...")
    
    # Set environment variables for the client
    env = os.environ.copy()
    env["MCP_SERVER_URL"] = "http://localhost:8000"  # Use localhost instead of container name
    env["ANTHROPIC_API_KEY"] = os.environ.get("ANTHROPIC_API_KEY")  # Pass through the API key
    
    client_cmd = ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
    
    try:
        # Change directory to the MCP client folder
        os.chdir("services/mcp-client")
        # Start the client process
        mcp_client = subprocess.Popen(
            client_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            env=env
        )
        
        # Log the client output
        logger.info("MCP Client started with PID: %s", mcp_client.pid)
        
        # Print the client output
        while True:
            output = mcp_client.stdout.readline()
            if not output and mcp_client.poll() is not None:
                break
            if output:
                print(f"MCP-CLIENT: {output.strip()}")
                
        # Log if client exits
        if mcp_client.poll() is not None:
            logger.warning("MCP Client exited with code: %s", mcp_client.returncode)
    
    except Exception as e:
        logger.error("Error starting MCP Client: %s", str(e))
    finally:
        # Change back to the root directory
        os.chdir("../..")

if __name__ == "__main__":
    # Run in a separate process to avoid blocking the main thread
    client_process = Process(target=run_mcp_client)
    client_process.daemon = True
    client_process.start()
    
    # Keep the script running
    try:
        logger.info("MCP Client runner is active. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        client_process.terminate()