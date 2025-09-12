from abs import ABC, abstractmethod

class DataConnector(ABC):
    @abstractmethod
    def read(self):
        pass
    @abstractmethod
    def transform(self, data):
        pass
    @abstractmethod
    def write(self, data)
        pass

    def run(self):
        raw = self.read()
        transformed = self.transformed()
        self.write(transformed)
