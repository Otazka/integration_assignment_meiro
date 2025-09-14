import os
import logging
import sys
from csv_connector import CSVConnector

# Configure logging for production
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting CSV Data Connector application")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("Loaded configuration from .env file")
    except ImportError:
        logger.warning("python-dotenv not installed, using environment variables and defaults")
    
    # Load configuration
    server_url = os.getenv("SHOWADS_API_URL")
    project_key = os.getenv("PROJECT_KEY")
    csv_filename = os.getenv("CSV_PATH", "data.csv")
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), csv_filename)
    batch_size = int(os.getenv("BATCH_SIZE", "10000"))
    
    # Validate required credentials
    if not server_url:
        logger.error("SHOWADS_API_URL not found in environment variables")
        raise ValueError("SHOWADS_API_URL must be set in .env file")
    if not project_key:
        logger.error("PROJECT_KEY not found in environment variables")
        raise ValueError("PROJECT_KEY must be set in .env file")
    
    logger.info("Configuration loaded successfully")
    logger.info(f"CSV Path: {csv_path}")
    logger.info(f"Server URL: {server_url}")
    logger.info(f"Project Key: {project_key[:8]}...")  # Mask sensitive data
    logger.info(f"Batch Size: {batch_size}")
    
    try:
        logger.info("Initializing CSV connector")
        connector = CSVConnector(csv_path, server_url, project_key, batch_size)
        
        logger.info("Starting data processing pipeline")
        connector.run()
        
        logger.info("Data connector completed successfully!")
        
    except Exception as e:
        logger.error(f"Data connector failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()