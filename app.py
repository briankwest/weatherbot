import requests
from flask import Flask
from signalwire_swaig.core import SWAIG, SWAIGArgument
from dotenv import load_dotenv
from urllib.parse import urlencode
from datetime import datetime, timedelta
import os

load_dotenv()
app = Flask(__name__)
swaig = SWAIG(app)

API_KEY = os.getenv("WEATHER_API_KEY")
USER_AGENT = "WeatherBot/1.1"

def get_lat_lon(city, state):
    headers = {"User-Agent": USER_AGENT}
    query = urlencode({"city": city, "state": state, "format": "json"})
    url = f"https://nominatim.openstreetmap.org/search?{query}"
    response = requests.get(url, headers=headers).json()
    if response:
        return response[0]['lat'], response[0]['lon']
    return None, None
def get_weather_data(endpoint, city, state, params=None):
    lat, lon = get_lat_lon(city, state)
    if lat and lon:
        url = f"http://api.weatherapi.com/v1/{endpoint}.json?key={API_KEY}&q={lat},{lon}"
        if params:
            for key, value in params.items():
                url += f"&{key}={value}"
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
    params = {"days": 3}
    response = get_weather_data("forecast", city, state, params)
    if response and "forecast" in response:
        forecast_data = response["forecast"]["forecastday"]
        forecast_summary = f"3-Day Forecast for {city}, {state}:\n"
        for day in forecast_data:
            date = day["date"]
            condition = day["day"]["condition"]["text"]
            max_temp = day["day"]["maxtemp_f"]
            min_temp = day["day"]["mintemp_f"]
            forecast_summary += f"{date}: {condition} with a high of {max_temp}°F and a low of {min_temp}°F.\n"
        return forecast_summary.strip(), {}
    return "Forecast data not found.", {}

@swaig.endpoint("Get Historical Weather",
    city=SWAIGArgument("string", "City name"),
    state=SWAIGArgument("string", "State abbreviation"))
def get_historical_weather(city, state, meta_data_token=None, meta_data=None):
    historical_data = {}
    for days_ago in range(1, 8):
        date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        params = {"dt": date}
        response = get_weather_data("history", city, state, params)
        if response and "forecast" in response:
            day_data = response["forecast"]["forecastday"][0]["day"]
            historical_data[date] = {
                "avgtemp_f": day_data["avgtemp_f"],
                "condition": day_data["condition"]["text"]
            }
    if historical_data:
        history_summary = f"Historical Weather for {city}, {state} (Past 7 Days):\n"
        for date, data in historical_data.items():
            history_summary += f"{date}: {data['condition']} with an average temperature of {data['avgtemp_f']}°F.\n"
        return history_summary.strip(), {}
    return "Historical weather data not found.", {}

@swaig.endpoint("Get Astronomy Data",
    city=SWAIGArgument("string", "City name"),
    state=SWAIGArgument("string", "State abbreviation"))
def get_astronomy_data(city, state, meta_data_token=None, meta_data=None):
    date = datetime.now().strftime('%Y-%m-%d')
    params = {"dt": date}
    response = get_weather_data("astronomy", city, state, params)
    if response and "astronomy" in response:
        astro = response["astronomy"]["astro"]
        sunrise = astro["sunrise"]
        sunset = astro["sunset"]
        moonrise = astro["moonrise"]
        moonset = astro["moonset"]
        moon_phase = astro["moon_phase"]
        return (f"Astronomy Data for {city}, {state} on {date}:\n"
                f"Sunrise: {sunrise}\n"
                f"Sunset: {sunset}\n"
                f"Moonrise: {moonrise}\n"
                f"Moonset: {moonset}\n"
                f"Moon Phase: {moon_phase}"), {}
    return "Astronomy data not found.", {}

@swaig.endpoint("Get Time Zone",
    city=SWAIGArgument("string", "City name"),
    state=SWAIGArgument("string", "State abbreviation"))
def get_timezone(city, state, meta_data_token=None, meta_data=None):
    response = get_weather_data("timezone", city, state)
    if response and "location" in response:
        tz_id = response["location"]["tz_id"]
        localtime = response["location"]["localtime"]
        return f"The time zone in {city}, {state} is {tz_id}. The current local time is {localtime}.", {}
    return "Timezone data not found.", {}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)