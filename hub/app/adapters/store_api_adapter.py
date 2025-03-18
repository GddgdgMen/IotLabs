import json
import logging
import requests
from typing import List
from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_gateway import StoreGateway
from config import STORE_API_BASE_URL

class StoreApiAdapter(StoreGateway):
    """
    Adapter class for interacting with the Store API.
    """

    def __init__(self, api_base_url: str = STORE_API_BASE_URL):
        self.api_base_url = api_base_url
        self.endpoint = f"{self.api_base_url}/processed_agent_data"

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]) -> bool:
        """
        Sends processed agent data to the Store API.

        Parameters:
            processed_agent_data_batch (List[ProcessedAgentData]): 
                The processed agent data to be saved.

        Returns:
            bool: True if the data is successfully saved, False otherwise.
        """
        if not processed_agent_data_batch:
            logging.warning("No data to send.")
            return False

        # Convert list of ProcessedAgentData objects to dictionaries
        payload = [data.model_dump() for data in processed_agent_data_batch]

        try:
            response = requests.post(self.endpoint, json=payload, timeout=5)
            response.raise_for_status()
            logging.info(f"Successfully sent {len(payload)} records to {self.endpoint}")
            return True
        except requests.RequestException as e:
            logging.error(f"Failed to send data to Store API: {e}")
            return False
