# Weather AI Agent

## Table of Contents
1. [Introduction](#introduction)
2. [Overview](#overview)
3. [API Information](#api-information)
4. [Features & Capabilities](#features--capabilities)
5. [Environment Setup](#environment-setup)
6. [Functions & Implementations](#functions--implementations)
7. [Sample Queries & Responses](#sample-queries--responses)
8. [System Prompt](#system-prompt)
9. [Conclusion](#conclusion)
10. [Appendix](#appendix)

## Introduction
The **Weather AI Agent** provides real-time and forecasted weather information for any U.S. city and state. Using **SignalWire AI Gateway (SWAIG)**, the agent integrates **WeatherAPI** and **Nominatim (OpenStreetMap)** to fetch and process weather data efficiently.

## API Information
- **WeatherAPI**: Provides real-time, forecast, historical, and astronomical weather data.
  - Documentation: [WeatherAPI Docs](https://www.weatherapi.com/docs/)
  - Free Tier Includes:
    - Current Weather
    - 3-Day Forecast
    - Historical Weather (7 Days)
    - Astronomy Data
    - Time Zone Data

- **Nominatim (OSM Geocoding)**: Converts city/state into latitude and longitude.
  - Documentation: [Nominatim Docs](https://nominatim.org/release-docs/latest/)

## Features & Capabilities
The AI Agent supports the following:
- **Current Weather**: Temperature, humidity, wind speed, conditions.
- **Weather Forecast**: Up to 3 days ahead.
- **Astronomy Data**: Sunrise, sunset, moon phase.
- **Historical Weather**: Past 7 days' weather.
- **Time Zone Information**: Get timezone details based on location.

## Environment Setup
To run the Weather AI Agent, set up your environment as follows:

### 1. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Create `.env` File
```ini
WEATHER_API_KEY=your_weatherapi_key
```

### 3. Run the AI Agent
```bash
python app.py
```

## Functions & Implementations

### **1. Get Current Weather**
#### OpenAI Tool Spec
```json
{
  "name": "get_current_weather",
  "description": "Retrieve current weather for a given city and state in the U.S.",
  "parameters": {
    "city": { "type": "string", "description": "City name" },
    "state": { "type": "string", "description": "State abbreviation (e.g., TX)" }
  }
}
```

### **2. Get 3-Day Forecast**
#### OpenAI Tool Spec
```json
{
  "name": "get_forecast",
  "description": "Retrieve a 3-day weather forecast for a given city and state in the U.S.",
  "parameters": {
    "city": { "type": "string", "description": "City name" },
    "state": { "type": "string", "description": "State abbreviation (e.g., TX)" }
  }
}
```

### **3. Get Historical Weather (7 Days)**
#### OpenAI Tool Spec
```json
{
  "name": "get_historical_weather",
  "description": "Retrieve historical weather data for the past 7 days for a given city and state in the U.S.",
  "parameters": {
    "city": { "type": "string", "description": "City name" },
    "state": { "type": "string", "description": "State abbreviation (e.g., TX)" }
  }
}
```

### **4. Get Astronomy Data**
#### OpenAI Tool Spec
```json
{
  "name": "get_astronomy_data",
  "description": "Retrieve astronomy data such as sunrise, sunset, and moon phases for a given city and state in the U.S.",
  "parameters": {
    "city": { "type": "string", "description": "City name" },
    "state": { "type": "string", "description": "State abbreviation (e.g., TX)" }
  }
}
```

### **5. Get Time Zone Information**

#### OpenAI Tool Spec
```json
{
  "name": "get_timezone",
  "description": "Retrieve timezone information for a given city and state in the U.S.",
  "parameters": {
    "city": { "type": "string", "description": "City name" },
    "state": { "type": "string", "description": "State abbreviation (e.g., TX)" }
  }
}
```

#### Python Implementation 
```python
import requests
from flask import Flask
from signalwire_swaig.core import SWAIG, SWAIGArgument
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
swaig = SWAIG(app)

API_KEY = os.getenv("WEATHER_API_KEY")
USER_AGENT = "WeatherBot/1.1"

def get_lat_lon(city, state):
    headers = {"User-Agent": USER_AGENT}
    url = f"https://nominatim.openstreetmap.org/search?city={city}&state={state}&format=json"
    response = requests.get(url, headers=headers).json()
    if response:
        return response[0]['lat'], response[0]['lon']
    return None, None

def get_weather_data(endpoint, city, state):
    lat, lon = get_lat_lon(city, state)
    if lat and lon:
        url = f"http://api.weatherapi.com/v1/{endpoint}.json?key={API_KEY}&q={lat},{lon}"
        return requests.get(url).json()
    return None

@swaig.endpoint("Get Current Weather",
    city=SWAIGArgument("string", "City name"),
    state=SWAIGArgument("string", "State abbreviation"))
def get_current_weather(city, state, meta_data_token=None, meta_data=None):
    response = get_weather_data("current", city, state)
    if response and "current" in response:
        return f"{city}, {state} is currently {response['current']['temp_f']}°F with {response['current']['condition']['text']}.", {}
    return "Weather data not found.", {}

@swaig.endpoint("Get 3-Day Forecast",
    city=SWAIGArgument("string", "City name"),
    state=SWAIGArgument("string", "State abbreviation"))
def get_forecast(city, state, meta_data_token=None, meta_data=None):
    response = get_weather_data("forecast", city, state)
    if response and "forecast" in response:
        return response["forecast"], {}
    return "Forecast data not found.", {}

@swaig.endpoint("Get Historical Weather",
    city=SWAIGArgument("string", "City name"),
    state=SWAIGArgument("string", "State abbreviation"))
def get_historical_weather(city, state, meta_data_token=None, meta_data=None):
    response = get_weather_data("history", city, state)
    if response and "history" in response:
        return response["history"], {}
    return "Historical weather data not found.", {}

@swaig.endpoint("Get Astronomy Data",
    city=SWAIGArgument("string", "City name"),
    state=SWAIGArgument("string", "State abbreviation"))
def get_astronomy_data(city, state, meta_data_token=None, meta_data=None):
    response = get_weather_data("astronomy", city, state)
    if response and "astronomy" in response:
        return response["astronomy"], {}
    return "Astronomy data not found.", {}

@swaig.endpoint("Get Time Zone",
    city=SWAIGArgument("string", "City name"),
    state=SWAIGArgument("string", "State abbreviation"))
def get_timezone(city, state, meta_data_token=None, meta_data=None):
    response = get_weather_data("timezone", city, state)
    if response and "location" in response:
        return response["location"], {}
    return "Timezone data not found.", {}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
```

## System Prompt
```
You are a weather AI assistant that provides weather updates, 3-day forecasts, historical weather for the past 7 days, astronomy data, and timezone information for any U.S. city and state. You use real-time and forecast data from WeatherAPI and geolocation from Nominatim to ensure accurate results. Your responses are concise, human-readable, and informative. When a user asks for weather information, greet them with a message detailing all the functionalities you offer.
```

## Conclusion
The Weather AI Agent provides accurate weather updates by integrating WeatherAPI and Nominatim for geolocation. It delivers real-time information, forecasts, and historical weather data efficiently.

## Appendix
- **API Rate Limits**: WeatherAPI free tier allows limited requests per minute.
- **Error Handling**: The agent gracefully handles invalid locations or API errors.

---

This `README.md` provides everything needed to deploy and use the Weather AI Agent. Let me know if you need modifications!

