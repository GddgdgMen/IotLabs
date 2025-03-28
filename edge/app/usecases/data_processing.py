from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData


def process_agent_data(
        agent_data: AgentData,
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface based on z-axis acceleration,
    and also process and include air quality data.
    """
    z_acceleration = agent_data.accelerometer.z

    if 14000 <= z_acceleration <= 18000:
        road_state = "Smooth road"
    elif (12000 <= z_acceleration < 14000) or (18000 < z_acceleration <= 20000):
        road_state = "Slight bumps"
    else:
        road_state = "Severe Potholes"



    return ProcessedAgentData(
        road_state=road_state,
        agent_data=agent_data,
    )