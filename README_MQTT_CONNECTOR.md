# MQTT Connector (gmqtt)

A small asyncio-based MQTT connector built on top of `gmqtt` for Python trading bots and other apps.

## Install

```bash
python -m pip install -r requirements.txt
```

## Example

```bash
export MQTT_HOST=test.mosquitto.org
export MQTT_PORT=1883
python -m examples.mqtt_example
```

## API

- MQTTConnector.start(auto_reconnect=True)
- MQTTConnector.stop()
- MQTTConnector.wait_connected(timeout=None)
- MQTTConnector.register_message_handler(handler)
- MQTTConnector.subscribe(topics, qos=0)
- MQTTConnector.publish(topic, payload, qos=0, retain=False)

See `mqtt_connector/connector.py` for full configuration via `MqttConfig` and optional TLS via `MqttTLSConfig`.