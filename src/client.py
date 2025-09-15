from typing import Any, Dict
from interface import AuthService, RequestHandler

class ApiClient:
    def __init__(self, server_url: str, auth_service: AuthService, request_handler: RequestHandler) -> None:
        self.server_url: str = server_url.rstrip("/")
        self.auth_service: AuthService = auth_service
        self.request_handler: RequestHandler = request_handler

    def request(self, method: str, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        token: str = self.auth_service.get_token()
        headers: Dict[str, str] = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        url: str = f"{self.server_url}/{endpoint.lstrip('/')}"
        response = self.request_handler.send(method, url, headers=headers, **kwargs)

        if getattr(response, "status_code", None) == 200 and not getattr(response, "text", "").strip():
            return {"status": "success", "message": "Operation completed successfully"}

        try:
            return response.json()
        except Exception:
            return {"status": "success", "message": getattr(response, "text", "")} 

    