from interfaces import IMessageHandler


class PrintMessageHandler(IMessageHandler):
    async def handle_message(self, topic: str, payload: str):
        print(f"[MQTT MESSAGE] Topic: {topic} | Payload: {payload}")
