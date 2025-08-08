import asyncio
import os
from mqtt_connector import MQTTConnector, MqttConfig


async def main() -> None:
    broker_host = os.getenv("MQTT_HOST", "test.mosquitto.org")
    broker_port = int(os.getenv("MQTT_PORT", "1883"))

    connector = MQTTConnector(
        MqttConfig(
            host=broker_host,
            port=broker_port,
            client_id="gmqtt-example-client",
            keepalive=30,
        )
    )

    def on_message(topic: str, payload: bytes, qos: int, retain: bool):
        print(f"[MSG] topic={topic} qos={qos} retain={retain} payload={payload.decode(errors='replace')}")

    connector.register_message_handler(on_message)

    await connector.start(auto_reconnect=True)
    await connector.wait_connected(timeout=10)

    await connector.subscribe([("test/connector/demo/#", 0)])

    # Publish a test message
    await connector.publish("test/connector/demo/hello", "hello world", qos=0, retain=False)

    # Keep running for a short time to receive messages
    await asyncio.sleep(10)

    await connector.stop()


if __name__ == "__main__":
    asyncio.run(main())