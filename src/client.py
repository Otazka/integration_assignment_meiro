from interface import AuthService, RequestHandler

class ApiClient:
    def __init__(self, server_url: str, auth_service: AuthService, request_handler: RequestHandler):
        self.server_url = server_url.rstrip("/")
        self.auth_service = auth_service
        self.request_handler = request_handler

    def request(self, method: str, endpoint: str, **kwargs):
        token = self.auth_service.get_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        url = f"{self.server_url}/{endpoint.lstrip('/')}"
        response = self.request_handler.send(method, url, headers=headers, **kwargs)
        
        if response.status_code == 200 and not response.text.strip():
            return {"status": "success", "message": "Operation completed successfully"}
        
        try:
            return response.json()
        except ValueError:
            return {"status": "success", "message": response.text}

    