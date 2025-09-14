import os
from csv_connector import CSVConnector

def main():
    # Try to load .env file if python-dotenv is available
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded configuration from .env file")
    except ImportError:
        print("python-dotenv not installed, using environment variables and defaults")
    server_url = os.getenv("SHOWADS_API_URL")
    project_key = os.getenv("PROJECT_KEY")
    csv_filename = os.getenv("CSV_PATH", "data.csv")
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), csv_filename)
    batch_size = int(os.getenv("BATCH_SIZE", "10000"))
    
    if not server_url:
        raise ValueError("SHOWADS_API_URL must be set in .env file")
    if not project_key:
        raise ValueError("PROJECT_KEY must be set in .env file")
    
    print("Starting CSV Data Connector...")
    print(f"CSV Path: {csv_path}")
    print(f"Server URL: {server_url}")
    print(f"Project Key: {project_key}")
    print(f"Batch Size: {batch_size}")
    print("-" * 50)
    
    try:
        connector = CSVConnector(csv_path, server_url, project_key, batch_size)
        connector.run()
        print("Data connector completed successfully!")
        
    except Exception as e:
        print(f"Data connector failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()