from datetime import datetime
from typing import List, Tuple

import pandas as pd

from datasource import ProcessedAgentData


class FileDatasource:
    def __init__(self, csv_file: str, user_id: int = 1):
        self.csv_file = csv_file
        self.user_id = user_id
        self.index = 0
        self._new_points = []
        self.data = self._load_data()

    def _load_data(self) -> List[ProcessedAgentData]:
        df = pd.read_csv(self.csv_file)
        processed_data = []

        for _, row in df.iterrows():
            # Convert accelerometer data to road state (simple threshold-based approach)
            magnitude = (row['X'] ** 2 + row['Y'] ** 2 + row['Z'] ** 2) ** 0.5

            road_state = "BUMP" if magnitude > 16650 else "POTHOLE" if magnitude > 16000 else "NORMAL"

            # Create fake GPS coordinates (for demonstration)
            base_lat, base_lon = 50.4501, 30.5234  # Kyiv coordinates
            lat = base_lat + (row['X'] / 1000)  # Simple offset based on accelerometer data
            lon = base_lon + (row['Y'] / 1000)

            processed_data.append(
                ProcessedAgentData(
                    road_state=road_state,
                    user_id=self.user_id,
                    x=float(row['X']),
                    y=float(row['Y']),
                    z=float(row['Z']),
                    latitude=lat,
                    longitude=lon,
                    timestamp=datetime.now()  # Use current time for demonstration
                )
            )
        return processed_data

    def get_new_points(self) -> List[Tuple[float, float, str]]:
        if self.index >= len(self.data):
            return []

        current_data = self.data[self.index]
        self.index += 1

        return [(
            current_data.latitude,
            current_data.longitude,
            current_data.road_state
        )]