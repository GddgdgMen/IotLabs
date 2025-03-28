import signal
import sys
import time
from typing import Optional

from paho.mqtt import client as mqtt_client

import config
from file_datasource import FileDatasource
from schema.aggregated_data_schema import AggregatedDataSchema
from schema.parking_schema import ParkingSchema


class MQTTApplication:
    def __init__(self):
        self.client: Optional[mqtt_client.Client] = None
        self.datasource: Optional[FileDatasource] = None
        self.is_running = True

    def connect_mqtt(self, broker: str, port: int) -> mqtt_client.Client:
        """Create and connect MQTT client"""
        print(f"CONNECT TO {broker}:{port}")

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print(f"Connected to MQTT Broker ({broker}:{port})!")
            else:
                print(f"Failed to connect {broker}:{port}, return code {rc}")
                sys.exit(rc)

        client = mqtt_client.Client()
        client.on_connect = on_connect

        try:
            client.connect(broker, port)
            client.loop_start()
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            sys.exit(1)

        return client

    def publish(self, client: mqtt_client.Client, topics: dict, datasource: FileDatasource, delay: float):
        """Publish data to multiple MQTT topics"""
        try:
            datasource.startReading()

            while self.is_running:
                time.sleep(delay)
                try:
                    agg_data, parking_data = datasource.read()

                    # Publish aggregated data
                    if agg_data:
                        msg = AggregatedDataSchema().dumps(agg_data)
                        result = client.publish(topics['aggregated'], msg)
                        if result[0] != 0:
                            print(f"Failed to send aggregated data to topic {topics['aggregated']}")

                    # Publish parking data
                    if parking_data:
                        msg = ParkingSchema().dumps(parking_data)
                        result = client.publish(topics['parking'], msg)
                        if result[0] != 0:
                            print(f"Failed to send parking data to topic {topics['parking']}")

                    if not agg_data and not parking_data:
                        print("No data available from datasource")
                        continue

                except Exception as e:
                    print(f"Error while reading/publishing data: {e}")

        except Exception as e:
            print(f"Error in publish loop: {e}")
        finally:
            print("\nStopping data publication...")
            datasource.stopReading()

    def cleanup(self, *args):
        """Cleanup resources before exit"""
        print("\nReceived stop signal. Cleaning up...")
        self.is_running = False

        if self.datasource:
            self.datasource.stopReading()

        if self.client:
            self.client.loop_stop()
            self.client.disconnect()

        sys.exit(0)

    def run(self):
        """Main application entry point"""
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)

        try:
            # Prepare mqtt client
            self.client = self.connect_mqtt(config.MQTT_BROKER_HOST, config.MQTT_BROKER_PORT)

            # Prepare datasource
            self.datasource = FileDatasource(
                "data/accelerometer.csv",
                "data/gps.csv",
                "data/parking.csv",
                batch_size=5
            )

            # Define topics for different data types
            topics = {
                'aggregated': config.MQTT_TOPIC,
                'parking': f"{config.MQTT_TOPIC}/parking"
            }

            # Infinity publish data
            self.publish(self.client, topics, self.datasource, config.DELAY)

        except Exception as e:
            print(f"Application error: {e}")
            self.cleanup()


if __name__ == "__main__":
    app = MQTTApplication()
    app.run()