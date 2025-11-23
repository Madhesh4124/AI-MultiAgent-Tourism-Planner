import google.generativeai as genai
import requests
import json
import difflib  # Required for fuzzy matching in PlacesAgent

# ==========================================
# 1. GEO SERVICE (Helper)
# ==========================================
class GeoService:
    def get_coordinates(self, city_name):
        """
        Converts a city name (e.g., 'Bangalore') into Lat/Lon using Nominatim API.
        """
        print(f"   📍 GeoService: Looking up coordinates for '{city_name}'...")
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": city_name,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "TourismAIIntern_StudentApp/1.0" 
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                print(f"   -> Found: {lat}, {lon}")
                return lat, lon
            else:
                return None, None
        except Exception as e:
            print(f"   ⚠️ Geo Error: {e}")
            return None, None

# ==========================================
# 2. WEATHER AGENT (Real)
# ==========================================
class WeatherAgent:
    def get_weather(self, lat, lon):
        """
        Fetches real weather data from Open-Meteo.
        """
        print(f"   ☁️ WeatherAgent: Fetching forecast...")
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "daily": "precipitation_probability_max",
            "timezone": "auto"
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            current = data.get("current_weather", {})
            daily = data.get("daily", {})
            
            temp = current.get("temperature")
            rain_prob = daily.get("precipitation_probability_max", [0])[0] if daily else 0
            
            return f"It is currently **{temp}°C** with a **{rain_prob}%** chance of rain."
        except Exception as e:
            return f"Error getting weather: {e}"

# ==========================================
# 3. PLACES AGENT (Advanced Logic)
# ==========================================
class PlacesAgent:
    def get_places(self, lat, lon):
        """
        Fetches top tourist attractions using Overpass API.
        Uses advanced scoring (Wikipedia/Wikidata) and fuzzy deduplication.
        """
        RADIUS = 10000  # 10 km radius
        print(f"   🏛️ PlacesAgent: Searching for top landmarks ({RADIUS/1000}km radius)...")
        
        url = "https://overpass-api.de/api/interpreter"

        # Query: Optimized for speed, filters by Tourism/Historic/Leisure
        query = f"""
        [out:json][timeout:25];
        (
          nwr["tourism"="attraction"](around:{RADIUS},{lat},{lon});
          nwr["tourism"="museum"](around:{RADIUS},{lat},{lon});
          nwr["tourism"="zoo"](around:{RADIUS},{lat},{lon});
          nwr["historic"="monument"](around:{RADIUS},{lat},{lon});
          nwr["historic"="memorial"](around:{RADIUS},{lat},{lon});
          nwr["historic"="castle"](around:{RADIUS},{lat},{lon});
          nwr["leisure"="park"](around:{RADIUS},{lat},{lon});
          nwr["leisure"="garden"](around:{RADIUS},{lat},{lon});
          nwr["amenity"="place_of_worship"]["tourism"](around:{RADIUS},{lat},{lon});
          nwr["natural"="peak"](around:{RADIUS},{lat},{lon});
          nwr["natural"="beach"](around:{RADIUS},{lat},{lon});
        );
        out center;
        """

        try:
            response = requests.post(url, data=query)
            data = response.json()
            elements = data.get("elements", [])

            results = []

            # A. FILTERS (Remove noise)
            skip_words = [
                "statue", "cross", "circle", "junction", "road", "stop",
                "office", "department", "association", "residential",
                "sector", "block", "phase", "extension", "canteen",
                "auditorium", "market", "mall", "parking", "entrance",
                "gate", "toilet", "restroom", "bus station", "bureau",
                "laboratoire", "swimming pool", "gym", 
                "robinier" # Skips specific famous trees in Paris that clog lists
            ]

            top_keywords = [
                "palace", "tower", "castle", "cathedral", "temple", "church",
                "mosque", "fort", "museum", "stadium", "garden", "park",
                "botanical", "zoo", "bridge", "opera", "aquarium", 
                "monument", "louvre", "eiffel", "taj mahal", "colosseum",
                "notre dame", "sacre-coeur", "arc de triomphe", "orsay",
                "vidhana soudha", "cubbon", "lalbagh"
            ]

            for el in elements:
                tags = el.get("tags", {})
                name = tags.get("name")
                if not name:
                    continue

                name_low = name.lower()

                # Skip noise
                if any(w in name_low for w in skip_words):
                    continue

                # B. SCORING SYSTEM (Lower score is better)
                score = 1000 

                # 1. Wikipedia/Wikidata is the strongest signal for "Famous"
                if "wikidata" in tags or "wikipedia" in tags:
                    score -= 400

                # 2. Keyword Boost
                if any(k in name_low for k in top_keywords):
                    score -= 150

                # 3. Data richness boost (more tags = usually more important)
                score -= len(tags) * 2

                # 4. Length Heuristic (Avoid super long administrative names)
                if len(name) < 40: 
                    score -= 10

                results.append({
                    "name": name,
                    "score": score
                })

            # Sort by best score first
            sorted_results = sorted(results, key=lambda x: x["score"])

            # C. FUZZY DEDUPLICATION
            final_places = []
            seen_names = []

            for item in sorted_results:
                nm = item["name"]
                
                # Optimization: Stop after finding 15 good places
                if len(final_places) >= 10:
                    break

                is_duplicate = False
                for existing in seen_names:
                    # 70% similarity check (e.g., "Eiffel Tower" vs "The Eiffel Tower")
                    if difflib.SequenceMatcher(None, nm.lower(), existing.lower()).ratio() > 0.7:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    seen_names.append(nm)
                    final_places.append(nm)

            if not final_places:
                return "No major tourist attractions found."

            return ", ".join(final_places)

        except Exception as e:
            return f"Error fetching places: {e}"

# ==========================================
# 4. PARENT AGENT (Orchestrator - Gemini Powered)
# ==========================================
class TourismParentAgent:
    def __init__(self, api_key):
        self.geo_service = GeoService()
        self.weather_agent = WeatherAgent()
        self.places_agent = PlacesAgent() # Now uses the ADVANCED logic
        
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.api_ready = True
        else:
            self.api_ready = False
            print("⚠️ Warning: API Key is missing.")

    def analyze_query_with_gemini(self, user_input):
        if not self.api_ready:
            return None

        prompt = f"""
        Analyze this query: "{user_input}"
        Extract:
        1. "city": Name of place.
        2. "wants_weather": true/false
        3. "wants_places": true/false
        Return JSON only.
        """
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception as e:
            print(f"LLM Error: {e}")
            return None

    def process_request(self, user_input):
        print(f"\n🔹 USER: '{user_input}'")
        
        if not self.api_ready:
            return "❌ API Key missing."

        # 1. Ask Gemini
        analysis = self.analyze_query_with_gemini(user_input)
        if not analysis or not analysis.get("city"):
            return "❌ Could not understand the query or find a city."
            
        city = analysis.get("city")
        print(f"🤖 Intent Detected: Weather={analysis['wants_weather']}, Places={analysis['wants_places']}")

        # 2. Get Coordinates (Needed for both Weather and Places)
        lat, lon = self.geo_service.get_coordinates(city)
        if not lat:
            return f"❌ I don't know where '{city}' is."

        results = [f"✅ **I found {city}!**"]

        # 3. Call Weather
        if analysis.get("wants_weather"):
            weather_info = self.weather_agent.get_weather(lat, lon)
            results.append(f"   -> {weather_info}")

        # 4. Call Places (Pass lat/lon, NOT city name)
        if analysis.get("wants_places"):
            places_info = self.places_agent.get_places(lat, lon)
            results.append(f"   -> Top Attractions: {places_info}")

        return "\n".join(results)


