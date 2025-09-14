import csv
import sys
import time
from typing import List, Dict, Iterator
from connector import DataConnector
from transform import validate_row, transform_row
from client import ApiClient
from getToken import APIToken
from request_handler import RequestHandler

class CSVConnector(DataConnector):
    def __init__(self, csv_path: str, server_url: str, project_key: str, batch_size: int = 1000):
        self.csv_path = csv_path
        self.batch_size = batch_size
        self.request_handler = RequestHandler(max_retries=3)
        self.auth_service = APIToken(server_url, project_key, self.request_handler)
        self.api_client = ApiClient(server_url, self.auth_service, self.request_handler)
        
    def read(self) -> Iterator[Dict]:
        print(f"Reading CSV file: {self.csv_path}")
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield row
    
    def transform(self, data: Iterator[Dict]) -> List[Dict]:
        print("Transforming and validating data...")
        transformed_rows = []
        total_rows = 0
        valid_rows = 0
        
        for row in data:
            total_rows += 1
            if validate_row(row):
                transformed_rows.append(transform_row(row))
                valid_rows += 1
        
        print(f"Processed {total_rows} rows, {valid_rows} valid rows")
        transformed_rows.sort(key=lambda x: x["customer_name"])
        print(f"Sorted {len(transformed_rows)} rows by customer_name")
        
        return transformed_rows
    
    def write(self, data: List[Dict]):
        print(f"Sending {len(data)} rows to server in batches of {self.batch_size}")
        
        total_sent = 0
        total_failed = 0
        
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(data) + self.batch_size - 1) // self.batch_size
            
            print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} rows)")
            
            try:
                bulk_data = []
                for row in batch:
                    bulk_data.append({
                        "VisitorCookie": row["customer_cookies"],
                        "BannerId": row["customer_banner_id"]
                    })
                
                # Send bulk request
                body = {"Data": bulk_data}
                response = self.api_client.request("POST", "banners/show/bulk", json=body)
                
                total_sent += len(batch)
                print(f"Successfully sent batch {batch_num} ({len(batch)} rows)")
                time.sleep(0.5)
                        
            except Exception as e:
                print(f"Failed to send batch {batch_num}: {e}")
                total_failed += len(batch)
        
        print(f"Data transfer completed: {total_sent} sent, {total_failed} failed")
