from __future__ import annotations

import asyncio
import ssl
import time
import uuid
from dataclasses import dataclass
from typing import Awaitable, Callable, Dict, Iterable, List, Optional, Tuple, Union

from gmqtt import Client as GmqttClient

MessageHandler = Callable[[str, bytes, int, bool], Union[None, Awaitable[None]]]


@dataclass
class MqttTLSConfig:
    cafile: Optional[str] = None
    capath: Optional[str] = None
    certfile: Optional[str] = None
    keyfile: Optional[str] = None
    cert_reqs: int = ssl.CERT_REQUIRED
    tls_version: Optional[int] = None
    ciphers: Optional[str] = None
    check_hostname: bool = True

    def build_ssl_context(self) -> ssl.SSLContext:
        context = ssl.create_default_context(cafile=self.cafile, capath=self.capath)
        if self.certfile and self.keyfile:
            context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
        if self.tls_version is not None:
            context.options |= self.tls_version  # type: ignore[operator]
        if self.ciphers:
            context.set_ciphers(self.ciphers)
        context.check_hostname = self.check_hostname
        context.verify_mode = self.cert_reqs
        return context


@dataclass
class MqttConfig:
    host: str
    port: int = 1883
    client_id: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    keepalive: int = 60
    clean_session: bool = True
    heartbeat_interval: int = 15
    reconnect_initial_delay: float = 1.0
    reconnect_max_delay: float = 60.0
    tls: Optional[MqttTLSConfig] = None
    will_topic: Optional[str] = None
    will_payload: Optional[Union[str, bytes]] = None
    will_qos: int = 0
    will_retain: bool = False


class MQTTConnector:
    def __init__(self, config: MqttConfig):
        self._config = config
        self._client = GmqttClient(client_id=config.client_id or f"client-{uuid.uuid4()}", clean_session=config.clean_session)
        self._connected_event = asyncio.Event()
        self._disconnect_event = asyncio.Event()
        self._should_run = False
        self._reconnect_task: Optional[asyncio.Task] = None
        self._message_handler: Optional[MessageHandler] = None
        self._subscriptions: List[Tuple[str, int]] = []

        if config.username and config.password:
            self._client.set_auth_credentials(config.username, config.password)

        if config.will_topic is not None and config.will_payload is not None:
            payload = config.will_payload.encode() if isinstance(config.will_payload, str) else config.will_payload
            self._client.set_will_message(
                config.will_topic,
                payload,
                config.will_qos,
                config.will_retain,
            )

        # Callbacks
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message
        self._client.on_subscribe = self._on_subscribe

    # Public API
    async def start(self, auto_reconnect: bool = True) -> None:
        self._should_run = True
        await self._connect_once()
        if auto_reconnect and self._reconnect_task is None:
            self._reconnect_task = asyncio.create_task(self._maintain_connection())

    async def stop(self) -> None:
        self._should_run = False
        if self._reconnect_task:
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass
            finally:
                self._reconnect_task = None
        await self._safe_disconnect()

    async def wait_connected(self, timeout: Optional[float] = None) -> bool:
        try:
            await asyncio.wait_for(self._connected_event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False

    def register_message_handler(self, handler: MessageHandler) -> None:
        self._message_handler = handler

    async def subscribe(self, topics: Union[str, Iterable[Union[str, Tuple[str, int]]]], qos: int = 0) -> None:
        if isinstance(topics, str):
            subscriptions: List[Tuple[str, int]] = [(topics, qos)]
        else:
            subscriptions = []
            for item in topics:
                if isinstance(item, tuple):
                    subscriptions.append((item[0], int(item[1])))
                else:
                    subscriptions.append((str(item), qos))

        # Save subscriptions for re-subscription after reconnect
        for topic, tqos in subscriptions:
            if (topic, tqos) not in self._subscriptions:
                self._subscriptions.append((topic, tqos))

        # If connected, subscribe right away
        if self._client.is_connected:
            for topic, tqos in subscriptions:
                self._client.subscribe(topic, qos=tqos)
        else:
            # Will be applied on next (re)connect
            pass

    async def publish(
        self,
        topic: str,
        payload: Union[str, bytes],
        qos: int = 0,
        retain: bool = False,
        content_type: Optional[str] = None,
    ) -> None:
        data = payload.encode() if isinstance(payload, str) else payload
        if content_type is None:
            self._client.publish(topic, data, qos=qos, retain=retain)
        else:
            self._client.publish(topic, data, qos=qos, retain=retain, content_type=content_type)

    # Internal
    async def _connect_once(self) -> None:
        ssl_ctx = self._config.tls.build_ssl_context() if self._config.tls else None
        await self._client.connect(
            host=self._config.host,
            port=self._config.port,
            keepalive=self._config.keepalive,
            ssl=ssl_ctx,
        )

    async def _safe_disconnect(self) -> None:
        if self._client.is_connected:
            await self._client.disconnect()
        self._connected_event.clear()

    async def _maintain_connection(self) -> None:
        delay = self._config.reconnect_initial_delay
        max_delay = self._config.reconnect_max_delay
        while self._should_run:
            # Wait for disconnect event
            await self._disconnect_event.wait()
            self._disconnect_event.clear()

            if not self._should_run:
                break

            # Exponential backoff reconnect loop
            while self._should_run and not self._client.is_connected:
                try:
                    await self._connect_once()
                    delay = self._config.reconnect_initial_delay
                    break
                except Exception:
                    await asyncio.sleep(delay)
                    delay = min(delay * 2.0, max_delay)

    # Callbacks
    def _on_connect(self, client: GmqttClient, flags, rc, properties):  # type: ignore[no-untyped-def]
        # Re-subscribe all stored subscriptions
        for topic, qos in self._subscriptions:
            client.subscribe(topic, qos=qos)
        self._connected_event.set()

    def _on_disconnect(self, client: GmqttClient, packet, exc=None):  # type: ignore[no-untyped-def]
        self._connected_event.clear()
        # Trigger reconnect loop
        self._disconnect_event.set()

    async def _dispatch_message(self, topic: str, payload: bytes, qos: int, retain: bool) -> None:
        if self._message_handler is None:
            return
        result = self._message_handler(topic, payload, qos, retain)
        if asyncio.iscoroutine(result):
            await result

    def _on_message(self, client: GmqttClient, topic: str, payload: bytes, qos: int, properties):  # type: ignore[no-untyped-def]
        # gmqtt invokes message callback in event loop; schedule our handler
        retain = getattr(properties, "retain", False) if properties is not None else False
        asyncio.create_task(self._dispatch_message(topic, payload, qos, retain))

    def _on_subscribe(self, client: GmqttClient, mid, qos, properties):  # type: ignore[no-untyped-def]
        # No-op hook for now; could add logging or metrics
        return None


__all__ = [
    "MQTTConnector",
    "MqttConfig",
    "MqttTLSConfig",
]