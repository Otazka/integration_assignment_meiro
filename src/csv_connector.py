import csv
import sys
import time
import os
import logging
from typing import List, Dict, Iterator
from connector import DataConnector
from transform import validate_row, transform_row
from client import ApiClient
from getToken import APIToken
from request_handler import RequestHandler

logger = logging.getLogger(__name__)

class CSVConnector(DataConnector):
    def __init__(self, csv_path: str, server_url: str, project_key: str, batch_size: int = 1000):
        logger.info(f"Initializing CSV connector with batch size: {batch_size}")
        self.csv_path = csv_path
        self.batch_size = batch_size
        max_retries = int(os.getenv("MAX_RETRIES", "3"))
        logger.info(f"Setting up request handler with max retries: {max_retries}")
        self.request_handler = RequestHandler(max_retries=max_retries)
        self.auth_service = APIToken(server_url, project_key, self.request_handler)
        self.api_client = ApiClient(server_url, self.auth_service, self.request_handler)
        logger.info("CSV connector initialized successfully")
        
    def read(self) -> Iterator[Dict]:
        logger.info(f"Reading CSV file: {self.csv_path}")
        try:
            with open(self.csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                row_count = 0
                for row in reader:
                    row_count += 1
                    if row_count % 1000 == 0:
                        logger.debug(f"Read {row_count} rows from CSV")
                    yield row
                logger.info(f"Finished reading CSV file. Total rows: {row_count}")
        except FileNotFoundError:
            logger.error(f"CSV file not found: {self.csv_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise
    
    def transform(self, data: Iterator[Dict]) -> List[Dict]:
        logger.info("Starting data transformation and validation")
        transformed_rows = []
        total_rows = 0
        valid_rows = 0
        
        for row in data:
            total_rows += 1
            if validate_row(row):
                transformed_rows.append(transform_row(row))
                valid_rows += 1
            else:
                logger.debug(f"Row {total_rows} failed validation: {row}")
        
        logger.info(f"Data transformation completed. Processed {total_rows} rows, {valid_rows} valid rows")
        logger.info("Sorting data by customer name")
        transformed_rows.sort(key=lambda x: x["customer_name"])
        logger.info(f"Data sorted successfully. {len(transformed_rows)} rows ready for processing")
        
        return transformed_rows
    
    def write(self, data: List[Dict]):
        logger.info(f"Starting data transfer. Sending {len(data)} rows to server in batches of {self.batch_size}")
        
        total_sent = 0
        total_failed = 0
        
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(data) + self.batch_size - 1) // self.batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} rows)")
            
            try:
                bulk_data = []
                for row in batch:
                    bulk_data.append({
                        "VisitorCookie": row["customer_cookies"],
                        "BannerId": row["customer_banner_id"]
                    })
                
                logger.debug(f"Prepared bulk data for batch {batch_num}: {len(bulk_data)} records")
                body = {"Data": bulk_data}
                
                logger.info(f"Sending batch {batch_num} to API")
                response = self.api_client.request("POST", "banners/show/bulk", json=body)
                
                total_sent += len(batch)
                logger.info(f"Successfully sent batch {batch_num} ({len(batch)} rows)")
                
                request_delay = float(os.getenv("REQUEST_DELAY", "0.5"))
                logger.debug(f"Waiting {request_delay}s before next batch")
                time.sleep(request_delay)
                        
            except Exception as e:
                logger.error(f"Failed to send batch {batch_num}: {e}")
                total_failed += len(batch)
        
        logger.info(f"Data transfer completed: {total_sent} sent, {total_failed} failed")
        if total_failed > 0:
            logger.warning(f"Some data transfer failed. {total_failed} rows were not sent successfully")
