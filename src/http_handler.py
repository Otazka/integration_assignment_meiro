import sys
sys.path.append("/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages")
import requests
import time
import random
import logging
from typing import Any
from interface import RequestHandler as BaseRequestHandler

logger = logging.getLogger(__name__)

class RequestHandler(BaseRequestHandler):
    def __init__(self, max_retries: int = 3) -> None:
        self.max_retries: int = max_retries
    
    def send(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        logger.debug(f"Sending {method} request to {url}")
        retries: int = 0
        
        while retries < self.max_retries:
            try:
                response: requests.Response = requests.request(method, url, **kwargs)
                logger.debug(f"Response status: {response.status_code}")
                
                if response.status_code in (500, 429):
                    wait_time: float = (2 ** retries) + random.uniform(0, 1)
                    logger.warning(f"Server error {response.status_code}, retrying in {wait_time:.1f}s (attempt {retries + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                    retries += 1
                    continue
                    
                response.raise_for_status()
                logger.debug(f"Request successful: {response.status_code}")
                return response
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                if retries < self.max_retries - 1:
                    wait_time: float = (2 ** retries) + random.uniform(0, 1)
                    logger.info(f"Retrying in {wait_time:.1f}s (attempt {retries + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                    retries += 1
                else:
                    raise
        
        # This should never be reached, but just in case
        response.raise_for_status()
        return response