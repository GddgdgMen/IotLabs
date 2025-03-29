import asyncio
import json
import websockets
from datetime import datetime
from kivy import Logger
from pydantic import BaseModel, field_validator
from config import STORE_HOST, STORE_PORT

class TrafficData(BaseModel):
    road_state: str
    user_id: int
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime

    @classmethod
    @field_validator("timestamp", mode="before")
    def validate_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except Exception:
            raise ValueError("Timestamp must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).")

class Datasource:
    def __init__(self, user_id: int):
        self._data_cache = []
        self.user_id = user_id
        self.connection_status = None

    def get_new_points(self):
        new_data = self._data_cache
        self._data_cache = []
        return new_data

    async def connect_to_server(self):
        endpoint = f"ws://{STORE_HOST}:{STORE_PORT}/ws/{self.user_id}"
        while True:
            try:
                async with websockets.connect(endpoint) as ws:
                    self.connection_status = "Connected"
                    while True:
                        message = await ws.recv()
                        parsed = json.loads(message)
                        self._process_data(parsed)
            except Exception as err:
                self.connection_status = "Disconnected"
                Logger.error(f"WebSocket error: {err}")
                await asyncio.sleep(5)

    def _process_data(self, raw_data):
        print(raw_data)
        Logger.debug(f"Data received: {raw_data}")
        parsed = TrafficData(**raw_data)
        self._data_cache.append((parsed.latitude, parsed.longitude, parsed.road_state))
