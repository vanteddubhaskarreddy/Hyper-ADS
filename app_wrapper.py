# Ensure patches are loaded before any other imports
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('app_wrapper')

# Add current directory to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger.info("Loading SQLite patch...")
# Import SQLite patch first
import sqlite3_patch

# Disable ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["ALLOW_RESET"] = "True"

# Check for required dependencies
try:
    logger.info("Checking for required dependencies...")
    import appdirs
    import chromadb
    import crewai
    logger.info("All dependencies loaded successfully")
except ImportError as e:
    logger.error(f"Missing dependency: {e}")
    raise

# Now import the Flask app
logger.info("Loading Flask application...")
from app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))