import streamlit as st
import requests

# 🔹 Replace with your PUBLIC backend URL when deploying
BACKEND_URL = "http://127.0.0.1:8000"  # Change to your server IP after deployment

st.set_page_config(page_title="SmartStore AI", page_icon="🛒", layout="wide")
st.title("🛒 SmartStore AI - Retail Robotics Simulation")

st.write(
    """
    Welcome! This is a simulation of a smart retail store with shelves and a robot.
    
    **How it works:**
    1. Shelves can become empty randomly (simulate customer purchases).  
    2. The robot decides which shelf to restock next.  
    3. Metrics track robot tasks and shelf status in real-time.
    """
)

# -------------------------
# GET STATE
# -------------------------
def get_state():
    try:
        response = requests.get(f"{BACKEND_URL}/state", timeout=5)
        response.raise_for_status()
        return response.json()["store"]
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {e}")
        return None

state = get_state()

if state:
    # -------------------------
    # SIMULATE EMPTY SHELF
    # -------------------------
    st.subheader("1️⃣ Simulate Shelf Activity")
    st.write("Click the button below to simulate a shelf becoming empty (like a customer bought items).")
    if st.button("Simulate Shelf Becoming Empty"):
        try:
            res = requests.post(f"{BACKEND_URL}/simulate_empty", timeout=5)
            res.raise_for_status()
            st.success(res.json()["message"])
        except requests.exceptions.RequestException as e:
            st.error(f"Error simulating empty shelf: {e}")

    # -------------------------
    # ASK AI DECISION
    # -------------------------
    st.subheader("2️⃣ Restock Decision")
    st.write("Click the button below to let the robot decide which shelf to restock next.")
    if st.button("Ask Robot to Restock"):
        try:
            response = requests.post(f"{BACKEND_URL}/decide", timeout=5)
            response.raise_for_status()
            result = response.json()
            if "decision" in result:
                st.success(f"🤖 Robot is restocking Shelf {result['decision']}")
            else:
                st.warning(result.get("message", "No empty shelves to restock"))
        except requests.exceptions.RequestException as e:
            st.error(f"Error making restock decision: {e}")

    # -------------------------
    # DISPLAY SHELVES
    # -------------------------
    st.subheader("📦 Shelf Status")
    st.write("Green = Full | Red = Empty")
    cols = st.columns(len(state["shelves"]))
    for i, (name, data) in enumerate(state["shelves"].items()):
        color = "🟢 Full" if data["status"] == "full" else "🔴 Empty"
        with cols[i]:
            st.markdown(f"### Shelf {name}")
            st.write(f"**Status:** {color}")
            st.write(f"**Traffic:** {data['traffic']}")
            st.write(f"**Empty Minutes:** {data['empty_minutes']}")

    # -------------------------
    # ROBOT STATUS
    # -------------------------
    st.subheader("🤖 Robot Status")
    st.write(f"The robot is currently at **Shelf {state['robot_position']}**")

    # -------------------------
    # METRICS
    # -------------------------
    st.subheader("📊 Tasks Completed")
    st.metric("Total Restocking Tasks", state["tasks_completed"])

    st.write("---")
    st.write("💡 **Tip:** Try simulating multiple empty shelves and see how the robot decides which one to restock first!")
