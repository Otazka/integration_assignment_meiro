import os
from csv_connector import CSVConnector

def main():
    server_url = "https://intg-engineer-server-929282497502.europe-west1.run.app"
    project_key = "helloworld"
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data.csv")
    batch_size = 10000
    
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