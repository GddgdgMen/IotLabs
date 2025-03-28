from typing import List

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from database import processed_agent_data
from models import ProcessedAgentData, ProcessedAgentDataInDB


def db_to_api_model(row) -> ProcessedAgentDataInDB:
    if row is None:
        return None
    return ProcessedAgentDataInDB(
        id=row.id,
        road_state=row.road_state,
        user_id=row.user_id,
        x=row.x,
        y=row.y,
        z=row.z,
        latitude=row.latitude,
        longitude=row.longitude,
        timestamp=row.timestamp,
        # add new
    )


def create_processed_data(db: Session, data_list: List[ProcessedAgentData]):
    values = []
    for item in data_list:
        agent_data = item.agent_data
        values.append(
            {
                "road_state": item.road_state,
                "user_id": agent_data.user_id,
                "x": agent_data.accelerometer.x,
                "y": agent_data.accelerometer.y,
                "z": agent_data.accelerometer.z,
                "latitude": agent_data.gps.latitude,
                "longitude": agent_data.gps.longitude,
                "timestamp": agent_data.timestamp,
                #add new
            }
        )
    result = db.execute(processed_agent_data.insert().returning(*processed_agent_data.c), values)
    db.commit()
    return [db_to_api_model(row) for row in result.all()]


def get_processed_data(db: Session, data_id: int):
    query = select(processed_agent_data).where(processed_agent_data.c.id == data_id)
    result = db.execute(query).first()
    return db_to_api_model(result)


def get_all_processed_data(db: Session):
    query = select(processed_agent_data)
    result = db.execute(query).all()
    return [db_to_api_model(row) for row in result]


def update_processed_data(db: Session, data_id: int, data: ProcessedAgentData):
    agent_data = data.agent_data
    values = {
        "road_state": data.road_state,
        "user_id": agent_data.user_id,
        "x": agent_data.accelerometer.x,
        "y": agent_data.accelerometer.y,
        "z": agent_data.accelerometer.z,
        "latitude": agent_data.gps.latitude,
        "longitude": agent_data.gps.longitude,
        "timestamp": agent_data.timestamp,
        # add new

    }
    query = processed_agent_data.update().where(processed_agent_data.c.id == data_id).values(values).returning(
        *processed_agent_data.c)
    result = db.execute(query).first()
    db.commit()
    return db_to_api_model(result)


def delete_processed_data(db: Session, data_id: int):
    query = delete(processed_agent_data).where(processed_agent_data.c.id == data_id).returning(*processed_agent_data.c)
    result = db.execute(query).first()
    db.commit()
    return db_to_api_model(result)