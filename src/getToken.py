import sys
sys.path.append("/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages")
import requests
import time
from interface import AuthService

class APIToken(AuthService):
    def __init__(self, server_url:str, project_key: str, request_handler):
        self.server_url = server_url.rstrip("/")
        self.project_key = project_key
        self.request_handler = request_handler
        self.access_token = None
        self.token_life = 0
        
    def auth(self):
        url = f"{self.server_url}/auth"
        body = {
            "ProjectKey": self.project_key
        }
        response = self.request_handler.send("POST", url, json=body)

        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("AccessToken")
            self.token_life = time.time() + (24*60*60)
            print("Successful! Token is: ", self.access_token)
        elif response.status_code == 400:
            print("Error 400: Bad request in case of invalid payload (missing or empty ProjectKey)")
        elif response.status_code == 429:
            print("Error 429: Too many Requests if the API is under heavy load")
        elif response.status_code == 500:
            print("Error 500: Internal server error if there is an error on the server side. The API is not always reliable.")
        else:
            print("Failed", response.status_code, response.text)
        return self.access_token
    
    def get_token(self) -> str:
        if not self.access_token or time.time() >= self.token_life:
            self.auth()
        return self.access_token

    
    




