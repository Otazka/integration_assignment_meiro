import sys
sys.path.append("/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages")
import requests
import time
import logging
from interface import AuthService

logger = logging.getLogger(__name__)

class APIToken(AuthService):
    def __init__(self, server_url:str, project_key: str, request_handler):
        self.server_url = server_url.rstrip("/")
        self.project_key = project_key
        self.request_handler = request_handler
        self.access_token = None
        self.token_life = 0
        
    def auth(self):
        logger.info("Starting authentication process")
        url = f"{self.server_url}/auth"
        body = {
            "ProjectKey": self.project_key
        }
        
        try:
            logger.debug(f"Authenticating with server: {url}")
            response = self.request_handler.send("POST", url, json=body)

            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("AccessToken")
                self.token_life = time.time() + (24*60*60)
                logger.info("Authentication successful")
                logger.debug(f"Token obtained: {self.access_token[:8]}...")
            elif response.status_code == 400:
                logger.error("Authentication failed: Bad request (invalid payload or missing ProjectKey)")
            elif response.status_code == 429:
                logger.warning("Authentication failed: Too many requests (API under heavy load)")
            elif response.status_code == 500:
                logger.error("Authentication failed: Internal server error")
            else:
                logger.error(f"Authentication failed with status {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Authentication request failed: {e}")
            
        return self.access_token
    
    def get_token(self) -> str:
        if not self.access_token or time.time() >= self.token_life:
            logger.info("Token expired or not available, refreshing authentication")
            self.auth()
        else:
            logger.debug("Using existing valid token")
        return self.access_token

    
    




