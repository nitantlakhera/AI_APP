import os
import requests
from dotenv import load_dotenv
from mcp.server import MCPServer

mcp = MCPServer("Weather Server")

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


# ============================================================
# REAL WEATHER TOOL
# ============================================================

@mcp.tool()
def get_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"]
    }


if __name__ == "__main__":
    mcp.run(
        "streamable-http",
        port=8003
    )
    # mcp.run()
