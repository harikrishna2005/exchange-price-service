class AuthenticationError(Exception):
    def __init__(self, message: str, broker_host: str = None, username: str = None, return_code: int = None):
        super().__init__(message)
        self.message = message
        self.broker_host = broker_host
        self.username = username
        self.return_code = return_code

    def __str__(self):
        parts = [f"[MQTT AuthenticationError] {self.message}"]
        if self.broker_host:
            parts.append(f"Broker: {self.broker_host}")
        if self.username:
            parts.append(f"User: {self.username}")
        if self.return_code is not None:
            parts.append(f"Return Code: {self.return_code}")
        return " | ".join(parts)


class SubscriptionError(Exception):
    def __init__(self, topic: str, qos: int = None, reason: str = ""):
        self.topic = topic
        self.qos = qos
        self.reason = reason
        super().__init__(f"Failed to subscribe to topic '{topic}' (QoS: {qos}) — {reason}")
