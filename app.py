import requests
from flask import Flask
from signalwire_swaig.core import SWAIG, SWAIGArgument
from dotenv import load_dotenv
from urllib.parse import urlencode
import os

load_dotenv()
app = Flask(__name__)
swaig = SWAIG(app)

API_KEY = os.getenv("WEATHER_API_KEY")
USER_AGENT = "WeatherBot/1.1"

from urllib.parse import urlencode

def get_lat_lon(city, state):
    headers = {"User-Agent": USER_AGENT}
    query = urlencode({"city": city, "state": state, "format": "json"})
    url = f"https://nominatim.openstreetmap.org/search?{query}"
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