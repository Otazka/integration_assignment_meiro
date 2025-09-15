from abc import ABC, abstractmethod
from typing import Any

class AuthService(ABC):
    @abstractmethod
    def get_token(self) -> str:
        pass

class RequestHandler(ABC):
    @abstractmethod
    def send(self, method: str, url: str, **kwargs: Any) -> Any:
        pass
