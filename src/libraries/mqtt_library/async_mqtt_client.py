import asyncio
from gmqtt import Client as MQTTClient, MQTTConnectError
from interfaces import IAsyncMqttClient, IMessageHandler
from typing import Callable, Awaitable
from exceptions_mqtt_user_defined import AuthenticationError, SubscriptionError


# ***************Sequence of Execution*****************
# await client.connect(host, port)
# Internally, gmqtt.connect() does:
# 1. Opens the socket connection
#
# 2. Performs the MQTT handshake
#
# 3. Once the broker accepts the connection, it triggers:
# self.client.on_connect(...)  # Your handler is called here

# So, the flow is:

# Your Code → await client.connect(...)
#                ↓
#       gmqtt connects to broker
#                ↓
#        MQTT CONNACK received
#                ↓
#     Your _on_connect handler is called

#
# | Method            | When it Executes                               |
# | ----------------- | ---------------------------------------------- |
# | `await connect()` | Starts the connection and waits until complete |
# | `_on_connect()`   | Triggered **after** successful connection      |
#


class AsyncGMqttConnector(IAsyncMqttClient):

    def __init__(self, client_id, host, port, username, password,
                 default_handler: Callable[[str, str], Awaitable[None]], clean_session=True):
        self.client_id = client_id
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.default_handler = default_handler

        self.client = MQTTClient(client_id=client_id, clean_session=clean_session)

        self.client.set_auth_credentials(username, password)

        # self.client.on_message = self._on_message
        self.client.on_connect = self._on_connect
        # self.client.on_disconnect = self._on_disconnect

        self._connected = asyncio.Event()
        self._topics = {}  # topic -> qos
        self._topic_handlers = {}  # topic -> handler
        print(f"[MQTT] Client initialized with ID: {client_id}, Host: {host}, Port: {port}")

    async def connect(self):
        retry_delay = 1
        while True:
            try:
                print(f"DELETE THIS --> connecting again and again ")
                await self.client.connect(self.host, self.port, keepalive=60)
                print(f"DELETE THIS --> Going to wait in the connect ")
                # await self._connected.wait()
                await asyncio.wait_for(self._connected.wait(), timeout=10)
                break
            except MQTTConnectError as e:
                print(f"[MQTT] Connect error: {e}")

                # # Detect MQTT connection codes 4 or 5 (invalid user/pass)
                # if getattr(e, 'return_code', None) in [0x87, 4, 5]:
                #     raise AuthenticationError(
                #         message="Authentication failed with broker",
                #         broker_host=self.host,
                #         username=self.username,
                #         return_code= getattr(e, 'return_code', None)
                #     ) from e

                # Optional: raise on any MQTTConnectError
                await self.disconnect()
                raise AuthenticationError(
                    message="Authentication failed with broker",
                    broker_host=self.host,
                    username=self.username,
                    return_code=getattr(e, 'return_code', None)
                ) from e
            except Exception as e:
                print(f"[MQTT] Connection failed: {e}, retrying in {retry_delay}s")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)
                if retry_delay == 60:
                    retry_delay = 1
                    print("[MQTT] Reached maximum retry delay, continuing to retry...")

    async def subscribe(self, topic: str, qos: int = 0, handler: Callable[[str], Awaitable[None]] = None):
        if topic not in self._topics:
            self._topics[topic] = qos
            if handler:
                self._topic_handlers[topic] = handler
            await self._connected.wait()
            try :
                self.client.subscribe(topic, qos)
            except Exception as e:
                raise SubscriptionError(topic, qos, str(e)) from e
            print(f"[MQTT] Subscribed to {topic} with QoS {qos}")

    async def unsubscribe(self, topic: str):
        if topic in self._topics:
            await self._connected.wait()
            self.client.unsubscribe(topic)
            del self._topics[topic]
            self._topic_handlers.pop(topic, None)
            print(f"[MQTT] Unsubscribed from {topic}")

    async def publish(self, topic: str, payload: str, qos: int = 0):
        await self._connected.wait()
        self.client.publish(topic, payload, qos=qos)

    async def disconnect(self):
        print(f"DELETE THIS --> Going to disconnect ")
        await self.client.disconnect()

    def _on_connect(self, client, flags, rc, properties):
        print("[MQTT] Connected")
        self._connected.set()

        async def resubscribe_all():
            for topic, qos in self._topics.items():
                client.subscribe(topic, qos)
                print(f"[MQTT] Re-subscribed to {topic} with QoS {qos}")
                if topic in self._topic_handlers:
                    print(f"[MQTT] Handler restored for {topic}")

        print(f"DELETE THIS --> Going to resubscribe all topics after SET connect")

        asyncio.create_task(resubscribe_all())

    async def _on_disconnect(self, client, packet, exc=None):
        print("[MQTT] Disconnected unexpectedly")
        self._connected.clear()
        # asyncio.create_task(self.connect())

    async def _on_message(self, client, topic, payload, qos, properties):
        handler = self._topic_handlers.get(topic, self.default_handler)
        await handler(topic, payload.decode())
