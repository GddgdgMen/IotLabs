import json
import logging
from datetime import datetime
from typing import List

import requests
from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_gateway import StoreGateway


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that knows how to handle datetime objects.
    When it encounters a datetime, it converts it to an ISO format string."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url
        self.logger = logging.getLogger(__name__)

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]) -> bool:
        """
        Save the processed road data to the Store API.
        Parameters:
            processed_agent_data_batch (List[ProcessedAgentData]): List of ProcessedAgentData objects.
        Returns:
            bool: True if the data is successfully saved, False otherwise.
        """
        url = f"{self.api_base_url}/processed_agent_data/"
        headers = {"Content-Type": "application/json"}

        try:
            # Convert the batch to a list of dictionaries
            data = [processed_data.model_dump() for processed_data in processed_agent_data_batch]
            # Use our custom encoder to handle datetime serialization
            json_data = json.dumps(data, cls=DateTimeEncoder)

            # Debug logging to see the serialized data
            self.logger.debug(f"Sending data to Store API: {json_data}")

        except TypeError as e:
            self.logger.error(f"Serialization error: {e}")
            return False

        try:
            response = requests.post(url, headers=headers, data=json_data)
            response.raise_for_status()
            self.logger.info(f"Data sent to Store API. Status code: {response.status_code}")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error sending data to Store API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response content: {e.response.content}")
            return False
