import sys
sys.path.append("/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages")
import requests
import time
import random
from interface import RequestHandler as BaseRequestHandler

class RequestHandler(BaseRequestHandler):
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
    
    def send(self, method: str, url: str, **kwargs):
        retries = 0
        while retries < self.max_retries:
            response = requests.request(method, url, **kwargs)
            if response.status_code in (500, 429):
                wait_time = (2 ** retries) + random.uniform(0, 1)
                print(f"{response.status_code}, retrying in {wait_time:.1f}s")
                time.sleep(wait_time)
                retries += 1
                continue
            response.raise_for_status()
            return response
        response.raise_for_status()
        return response