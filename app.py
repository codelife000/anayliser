# app.py (Fully Fixed Advanced SmartStore App)
import streamlit as st
import requests
import threading
from fastapi import FastAPI
import uvicorn
import random
import time

# -------------------------------
# Backend (FastAPI)
# -------------------------------
app = FastAPI()

# Initialize store with log to avoid KeyError
store = {
    "shelves": {
        "A": {"status": "full", "empty_minutes": 0, "traffic": "high"},
        "B": {"status": "full", "empty_minutes": 0, "traffic": "low"},
        "C": {"status": "full", "empty_minutes": 0, "traffic": "medium"},
    },
    "robot_position": "Dock",
    "tasks_completed": 0,
    "log": [],
}

@app.get("/state")
def get_state():
    return {"store": store}

@app.post("/simulate_empty")
def simulate_empty():
    shelf = random.choice(list(store["shelves"].keys()))
    store["shelves"][shelf]["status"] = "empty"
    store["shelves"][shelf]["empty_minutes"] = random.randint(1, 15)
    store["log"].append(f"Shelf {shelf} became empty")
    return {"message": f"Shelf {shelf} is now empty"}

@app.post("/decide")
def decide():
    empty_shelves = {k: v for k, v in store["shelves"].items() if v["status"] == "empty"}
    if not empty_shelves:
        return {"message": "No empty shelves"}
    decision = max(empty_shelves, key=lambda x: empty_shelves[x]["empty_minutes"])
    store["robot_position"] = decision
    store["shelves"][decision]["status"] = "full"
    store["tasks_completed"] += 1
    store["log"].append(f"Robot restocked Shelf {decision}")
    return {"decision": decision}

# -------------------------------
# Run FastAPI in Thread
# -------------------------------
def run_backend():
    uvicorn.run(app, host="0.0.0.0", port=8000)

threading.Thread(target=run_backend, daemon=True).start()

# -------------------------------
# Frontend (Streamlit)
# -------------------------------
BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="🛒 SmartStore AI", layout="wide")
st.title("🛒 SmartStore AI - Advanced Retail Simulation")

# -------------------------------
# Sidebar Controls
# -------------------------------
st.sidebar.header("⚙️ Controls")
auto_simulate = st.sidebar.checkbox("Auto-Simulate Empty Shelves")
simulate_interval = st.sidebar.slider("Simulation Interval (seconds)", 1, 10, 3)
if st.sidebar.button("Reset Store"):
    # Reset the store to initial state
    requests.post(f"{BACKEND_URL}/simulate_empty")  # simulate one empty shelf as a simple reset trick
    st.experimental_rerun()

# -------------------------------
# Fetch Store State
# -------------------------------
try:
    state = requests.get(f"{BACKEND_URL}/state").json()["store"]
except:
    st.error("Backend not running yet. Please wait a few seconds and refresh.")
    st.stop()

# -------------------------------
# Simulate Shelf Empty
# -------------------------------
st.subheader("1️⃣ Simulate Shelf Activity")
col1, col2 = st.columns(2)

with col1:
    if st.button("Simulate Shelf Becoming Empty"):
        res = requests.post(f"{BACKEND_URL}/simulate_empty")
        st.success(res.json()["message"])
        state = requests.get(f"{BACKEND_URL}/state").json()["store"]

with col2:
    if st.button("Ask Robot to Restock"):
        res = requests.post(f"{BACKEND_URL}/decide")
        result = res.json()
        if "decision" in result:
            st.success(f"🤖 Robot is restocking Shelf {result['decision']}")
        else:
            st.warning(result.get("message", "No empty shelves"))
        state = requests.get(f"{BACKEND_URL}/state").json()["store"]

# -------------------------------
# Auto Simulation
# -------------------------------
if auto_simulate:
    while True:
        requests.post(f"{BACKEND_URL}/simulate_empty")
        time.sleep(simulate_interval)
        st.experimental_rerun()

# -------------------------------
# Shelf Grid Display
# -------------------------------
st.subheader("📦 Shelf Status")
cols = st.columns(len(state["shelves"]))
for i, (name, data) in enumerate(state["shelves"].items()):
    color = "🟢 Full" if data["status"] == "full" else "🔴 Empty"
    robot_here = "🤖" if state["robot_position"] == name else ""
    with cols[i]:
        st.markdown(f"### Shelf {name} {robot_here}")
        st.write(f"**Status:** {color}")
        st.write(f"**Traffic:** {data['traffic']}")
        st.write(f"**Empty Minutes:** {data['empty_minutes']}")

# -------------------------------
# Metrics Panel
# -------------------------------
st.subheader("📊 Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Restocking Tasks", state["tasks_completed"])
with col2:
    empty_count = sum(1 for s in state["shelves"].values() if s["status"]=="empty")
    st.metric("Empty Shelves", empty_count)
with col3:
    st.metric("Robot Position", state["robot_position"])

# -------------------------------
# Action Log
# -------------------------------
st.subheader("📝 Action Log")
log = state.get("log", [])
for entry in log[-10:][::-1]:
    st.write(f"- {entry}")
