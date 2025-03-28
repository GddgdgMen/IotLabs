from typing import Set, Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from crud import (
    create_processed_data,
    get_processed_data,
    get_all_processed_data,
    update_processed_data,
    delete_processed_data,
)
from database import SessionLocal
from models import ProcessedAgentData, ProcessedAgentDataInDB

app = FastAPI()

# WebSocket subscriptions
subscriptions: Dict[int, Set[WebSocket]] = {}


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    if user_id not in subscriptions:
        subscriptions[user_id] = set()
    subscriptions[user_id].add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscriptions[user_id].remove(websocket)


async def send_data_to_subscribers(user_id: int, data: ProcessedAgentDataInDB):
    if user_id in subscriptions:
        for websocket in subscriptions[user_id]:
            try:
                data_dict = data.model_dump()
                data_dict['timestamp'] = data_dict['timestamp'].isoformat()
                await websocket.send_json(data_dict)
            except WebSocketDisconnect:
                subscriptions[user_id].remove(websocket)
            except Exception as e:
                print(f"Error sending data to websocket: {e}")
                continue


@app.post("/processed_agent_data/", response_model=List[ProcessedAgentDataInDB])
async def create_processed_agent_data(data: List[ProcessedAgentData]):
    db = SessionLocal()
    try:
        result = create_processed_data(db, data)
        for item in result:
            await send_data_to_subscribers(item.user_id, item)
        return result
    finally:
        db.close()


@app.get("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def read_processed_agent_data(processed_agent_data_id: int):
    db = SessionLocal()
    try:
        return get_processed_data(db, processed_agent_data_id)
    finally:
        db.close()


@app.get("/processed_agent_data/", response_model=List[ProcessedAgentDataInDB])
def list_processed_agent_data():
    db = SessionLocal()
    try:
        return get_all_processed_data(db)
    finally:
        db.close()


@app.put("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData):
    db = SessionLocal()
    try:
        return update_processed_data(db, processed_agent_data_id, data)
    finally:
        db.close()


@app.delete("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def delete_processed_agent_data(processed_agent_data_id: int):
    db = SessionLocal()
    try:
        return delete_processed_data(db, processed_agent_data_id)
    finally:
        db.close()
