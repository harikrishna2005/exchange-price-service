from abc import ABC, abstractmethod


class IAsyncMqttClient(ABC):
    @abstractmethod
    async def connect(self): pass

    @abstractmethod
    async def publish(self, topic: str, payload: str): pass

    @abstractmethod
    async def subscribe(self, topic: str): pass

    @abstractmethod
    async def disconnect(self): pass


class IMessageHandler(ABC):
    @abstractmethod
    async def handle_message(self, topic: str, payload: str): pass
