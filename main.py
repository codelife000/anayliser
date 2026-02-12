from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI()

# In-memory store
store = {
    "shelves": {
        "A": {"status": "full", "empty_minutes": 0, "traffic": "high"},
        "B": {"status": "full", "empty_minutes": 0, "traffic": "low"},
        "C": {"status": "full", "empty_minutes": 0, "traffic": "medium"},
    },
    "robot_position": "Dock",
    "tasks_completed": 0,
}

class DecisionRequest(BaseModel):
    shelves: dict

@app.get("/")
def root():
    return {"message": "SmartStore Backend Running"}  # JSON object

@app.get("/state")
def get_state():
    return {"store": store}  # JSON object

@app.post("/simulate_empty")
def simulate_empty():
    shelf = random.choice(list(store["shelves"].keys()))
    store["shelves"][shelf]["status"] = "empty"
    store["shelves"][shelf]["empty_minutes"] = random.randint(1, 15)
    return {"message": f"Shelf {shelf} is now empty"}  # JSON object

@app.post("/decide")
def decide():
    empty_shelves = {k: v for k, v in store["shelves"].items() if v["status"] == "empty"}

    if not empty_shelves:
        return {"message": "No empty shelves"}

    # Pick shelf with highest empty_minutes
    decision = max(empty_shelves, key=lambda x: empty_shelves[x]["empty_minutes"])

    store["robot_position"] = decision
    store["shelves"][decision]["status"] = "full"
    store["tasks_completed"] += 1

    return {"decision": decision}  # JSON object
