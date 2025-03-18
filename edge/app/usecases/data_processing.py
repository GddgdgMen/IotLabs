from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData

def classify_road_condition(z_acceleration: float) -> str:
    """
    Classifies the road condition based on the Z-axis acceleration value.
    """
    if -0.2 <= z_acceleration <= 0.2:
        return "Smooth Road"
    elif 0.2 < abs(z_acceleration) <= 0.5:
        return "Minor Bumps"
    elif 0.5 < abs(z_acceleration) <= 1.0:
        return "Rough Road"
    else:
        return "Severe Potholes"

def process_agent_data(agent_data: AgentData) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    """
    road_condition = classify_road_condition(agent_data.accelerometer.z)
    
    return ProcessedAgentData(
        timestamp=agent_data.timestamp,
        latitude=agent_data.gps.latitude,
        longitude=agent_data.gps.longitude,
        road_condition=road_condition
    )
