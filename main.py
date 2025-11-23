import streamlit as st
from dotenv import load_dotenv
import os
from main_agents import TourismParentAgent
import time

# ----------------------------------------------------
# Load API Key from .env
# ----------------------------------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# ----------------------------------------------------
# UI Setup
# ----------------------------------------------------
st.set_page_config(page_title="AI Tourism Planner", page_icon="🧭", layout="centered")

st.title("🧭 AI Tourism Multi-Agent Planner")
st.write("""
Enter anything like:

- “*I want to visit Bangalore, what are the places?*”
- “*What’s the weather in London?*”
- “*Plan my trip to Tokyo*”
- “*Tell me attractions in Paris + weather*”
""")

# ----------------------------------------------------
# Initialize Parent Agent
# ----------------------------------------------------
if not API_KEY:
    st.error("❌ GEMINI_API_KEY missing in .env!")
else:
    agent = TourismParentAgent(API_KEY)

# ----------------------------------------------------
# User Input
# ----------------------------------------------------
user_query = st.text_area("Ask something:", height=120)

def format_response(text):


    lines = text.split("\n")
    md = ""

    for line in lines:
        clean = line.strip()

        # ❌ Skip "I found <city>!"
        if clean.startswith("✅ I found"):
            continue

        # Weather section
        if "-> It is currently" in clean:
            md += "### 🌦 Weather\n"
            md += clean.replace("->", "").strip() + "\n"
            continue
        
        # Places section
        if "-> Top Attractions:" in clean:
            md += "### 🏛️ Top Attractions\n"
            places_text = clean.split("Top Attractions:")[1].strip()
            places = [p.strip() for p in places_text.split(",")]
            for p in places:
                md += f"- {p}\n"
            continue

        # Anything else
        if clean and not clean.startswith("->"):
            md += clean + "\n"

    return md



# ----------------------------------------------------
# Process Button
# ----------------------------------------------------
if st.button("Process My Query"):
    if not user_query.strip():
        st.warning("⚠️ Please enter a query.")
    else:
        with st.spinner("Thinking... 🤖"):
            raw_result = agent.process_request(user_query)

        formatted = format_response(raw_result)
        st.markdown(formatted)



