from paho.mqtt import client as mqtt_client
import json
import time
from schema.aggregated_data_schema import AggregatedDataSchema
from file_datasource import FileDatasource
import config

def connect_mqtt(broker, port):
    """Create MQTT client"""
    print(f"CONNECT TO {broker}:{port}")

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"✅ Connected to MQTT Broker ({broker}:{port})!")
        else:
            print(f"❌ Failed to connect {broker}:{port}, return code {rc}")
            exit(rc)

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()
    return client

def publish(client, topic, datasource, delay):
    datasource.startReading()

    while True:
        time.sleep(delay)
        data_batch = datasource.read()

        for data in data_batch:
            msg = AggregatedDataSchema().dumps(data)
            result = client.publish(topic, msg)

            status = result[0]
            if status == 0:
                print(f"✅ Sent `{msg}` to `{topic}`")
            else:
                print(f"❌ Failed to send message to `{topic}`")

def run():
    # Підключення до MQTT брокера
    client = connect_mqtt(config.MQTT_BROKER_HOST, config.MQTT_BROKER_PORT)

    # Джерело даних (передаємо файли акселерометра, GPS та паркінгу)
    datasource = FileDatasource(
        "data/accelerometer.csv", "data/gps.csv", "data/parking.csv", batch_size=5
    )

    # Відправка даних у MQTT
    publish(client, config.MQTT_TOPIC, datasource, config.DELAY)

if __name__ == '__main__':
    run()
