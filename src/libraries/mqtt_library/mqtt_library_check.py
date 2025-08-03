import asyncio

from async_mqtt_client import AsyncGMqttConnector
from handlers import PrintMessageHandler
from exceptions_mqtt_user_defined import AuthenticationError


async def main():
    # Define the MQTT broker host
    MQTT_BROKER_HOST = '3.110.54.115'
    # MQTT_BROKER_HOST = 'broker.emqx.io'
    MQTT_BROKER_PORT = '1883'
    MQTT_BROKER_USERNAME = ''
    MQTT_BROKER_PASSWORD = ''

    # Create an instance of the connector
    # connector = AsyncMQTTConnector(MQTT_BROKER_HOST, client_id="my-async-client-app")
    default_handler = PrintMessageHandler()
    connector = AsyncGMqttConnector(client_id="my-async-client-app", host=MQTT_BROKER_HOST,
                                    port=MQTT_BROKER_PORT,
                                    username=MQTT_BROKER_USERNAME,
                                    password=MQTT_BROKER_PASSWORD,
                                    default_handler=default_handler.handle_message,
                                    clean_session=True)
    try:
        await connector.connect()
    except AuthenticationError as e:
        print(str(e))
        # Optional: retry with fallback credentials or notify user

    # Subscribe to topics
    # await connector.subscribe("home/sensor/temperature", qos=1)
    # await connector.subscribe("home/alerts", qos=0)
    #
    # # Optionally publish a message
    # await connector.publish("home/sensor/temperature", "24.5°C")
    # Keep running
    try:
        while True:
            print(f'waiting for 10 seconds...')
            await asyncio.sleep(10)

    except asyncio.CancelledError:
        await connector.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
