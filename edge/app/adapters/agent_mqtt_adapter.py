from datetime import datetime
import logging
import paho.mqtt.client as mqtt
from app.interfaces.agent_gateway import AgentGateway
from app.entities.agent_data import AgentData, GpsData
from app.usecases.data_processing import process_agent_data
from app.interfaces.hub_gateway import HubGateway
import json


class AgentMQTTAdapter(AgentGateway):
    def __init__(
        self,
        broker_host,
        broker_port,
        topic,
        hub_gateway: HubGateway,
        batch_size=10,
    ):
        self.batch_size = batch_size
        # MQTT
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic
        self.client = mqtt.Client()
        # Hub
        self.hub_gateway = hub_gateway

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT broker")
            self.client.subscribe(self.topic)
        else:
            logging.info(f"Failed to connect to MQTT broker with code: {rc}")

    def on_message(self, client, userdata, msg):
        """Processing agent data and sent it to hub gateway"""
        try:
            payload: str = msg.payload.decode("utf-8")
            agent_data = AgentData.model_validate_json(payload, strict=True)
            parsed_data = json.loads(payload)
            accelerometer_data = parsed_data['accelerometer']
            gps_data = parsed_data['gps']
            timestamp_str = parsed_data['timestamp']
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            agent_data = AgentData(
                user_id=parsed_data['user_id'],
                accelerometer=accelerometer_data,
                gps=gps_data,
                timestamp=timestamp
            )
            processed_data = process_agent_data(agent_data)
            if not self.hub_gateway.save_data(processed_data):
                logging.error("Hub is not available")
        except Exception as e:
            logging.info(f"Error processing MQTT message: {e}")


    def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_host, self.broker_port, 60)

    def start(self):
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()