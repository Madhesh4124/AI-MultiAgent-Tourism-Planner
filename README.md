AI Multi-Agent Tourism Planner Assistant

A smart, multi-agent tourism planner powered by Google Gemini, OpenStreetMap, and Streamlit — designed to intelligently parse natural language queries and deliver weather forecasts + curated tourist attractions in real time.

This project was built as part of the Inkle AI Internship Assignment.

📖 Problem Statement

Goal: Build a Tourism Multi-Agent System where:

A Parent Agent understands user queries using LLMs.

Delegates tasks to Weather Agent & Places Agent.

Fetches data from free open-source APIs (no Google Maps).

Handles errors & unknown cities gracefully.

Returns useful results, not raw map data noise.

🏗️ System Architecture

The project follows a Manager → Worker / Tool pattern.

🧠 1. Parent Agent (Orchestrator – Gemini 2.0 Flash)

Responsible for:

Intent detection.

Extracting city name.

Deciding: wants_weather? and wants_places?.

Routing requests to child agents.

Formatting the final response.

Example: "I’m going to Rome, is it raining there and what are the top attractions?"

→ Detects both weather + places.

☁️ 2. Weather Agent (Open-Meteo API)

Features: Real-time temperature, Rain probability, Timezone aware.

No API Key Required.

Input: (lat, lon)

Output: "It is currently 18°C with a 20% chance of rain."

🏛️ 3. Places Agent (Overpass API)

Uses OpenStreetMap + a custom intelligence layer.

Features:

10km radius attraction search.

Keyword scoring (museum, palace, fort, garden, etc.).

Wikidata/Wikipedia boost (signals global importance).

Data richness scoring (more tags = more important).

Noise filtering (removes bus stops, statues, admin offices).

Fuzzy deduplication (removes duplicates like “Eiffel Tower” & “Tour Eiffel”).

Returns Clean, Curated Results ✅

Filters Out Noise ❌

Cubbon Park

"XYZ Bus Stop"

Lalbagh Botanical Garden

"Some Statue"

Bangalore Palace

"Office of..."

Visvesvaraya Museum

"Sector 4 Block"

Vidhana Soudha

"Public Toilet"

🎨 Streamlit App (Front-End)

The UI provides:

A clean input box.

Real-time results.

Weather & attractions formatted clearly.

No clutter like “Response:” or debug logs.

Users simply type:

"I want to visit Bangalore, what are the places?"

"What's the weather in New York?"

"Plan a trip to Tokyo."

...and the system responds beautifully.

🚀 Technical Highlights

🧠 1. LLM Intent Parser

Gemini identifies: City name, Weather intent, Places intent, and Mixed intent (both).

🎚️ 2. Intelligent Ranking Engine

Places are ranked using:

Wikipedia signals (High priority).

Keyword boosts (Palace, Fort, Museum > Park > Statue).

Tag count richness.

Popularity heuristics.

🔄 3. Fuzzy Deduplication

Uses difflib to avoid duplicate results.

🧼 4. Noise Filtering

Automatically removes: Statues, Crosses, Markets, Offices, Auditoriums, Bus stations, Residential blocks.

🛠️ Installation & Setup

1️⃣ Clone the repo

git clone https://github.com/Madhesh4124/AI-MultiAgent-Tourism-Planner.git
cd ai-tourism-agent


2️⃣ Install dependencies

pip install -r requirements.txt


3️⃣ Create .env

Create a file named .env in the root directory and add your key:

GEMINI_API_KEY=your_key_here


4️⃣ Run the Streamlit app

streamlit run main.py


App will open at: 👉 http://localhost:8501

🚀 Deploying to Streamlit Cloud (Free)

Push your project to GitHub

git init
git add .
git commit -m "Initial commit - AI Tourism Agent"
git branch -M main
git remote add origin [https://github.com/yourusername/ai-tourism-agent.git](https://github.com/yourusername/ai-tourism-agent.git)
git push -u origin main


Go to Streamlit Cloud
Visit share.streamlit.io.

Create New App

Repo → your repo

Branch → main

File → main.py

Add Secrets

Go to App → Settings → Secrets

Paste:

GEMINI_API_KEY="your_key_here"


Click Save. The app deploys automatically.

💻 Example Queries

“I want to visit Bangalore, what are the places?”

“Weather in New York?”

“Paris weather + tourist spots?”

“Plan a trip to Tokyo.”

“What’s cool to see in Mumbai?”

“Is Paris warmer than London?” (multi-city attempt)

🧪 Test Cases Covered

✅ Typos (“Bengluru”)

✅ Slang (“Bro, what’s cool in Mumbai”)

✅ Unexpected inputs (“Weather nearby?”)

✅ Unknown cities (“Gotham City”)

✅ Non-English names (“München”)

✅ Mixed intent queries

✅ Single intent queries

🔮 Future Improvements

Generate day-wise itineraries.

Add hotel/flight lookup (mock API).

Add map visualization (Folium).

Add image fetching via Wikipedia API.

Add caching for speed.

Support multi-city comparison (Paris vs London).
