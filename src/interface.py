from abc import ABC, abstractmethod

class AuthService(ABC):
    @abstractmethod
    def get_token(self) -> str:
        pass

class RequestHandler(ABC):
    @abstractmethod
    def send(self, method: str, url: str, **kwargs):
        pass
