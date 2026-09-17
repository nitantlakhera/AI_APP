import requests
from mcp.server import MCPServer

mcp = MCPServer("Weather Server")


@mcp.tool()
def get_weather(city: str) -> dict:
    """
        Get weather information for a city.
    """

    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "q": city,
            "appid": "89ed60064afaa0a0d0a16f5e2bf17559",
            "units": "metric"
        }
    )

    data = response.json()

    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "condition": data["weather"][0]["description"]
    }


@mcp.tool()
def get_exchange_rate(from_currency: str, to_currency: str) -> dict:
    rates = {
        "USD_INR": 88.0,
        "EUR_INR": 103.0,
        "GBP_INR": 119.0,
        "INR_USD": 0.0114,
        "INR_EUR": 0.0097,
        "INR_GBP": 0.0084
    }

    key = f"{from_currency.upper()}_{to_currency.upper()}"

    if key not in rates:
        return {
            "error": f"Exchange rate not available for {from_currency} to {to_currency}"
        }

    return {
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "rate": rates[key]
    }


# mcp run AI_AGENTS\weather_server.py --transport streamable-http
# mcp dev AI_AGENTS\weather_server.py --transport streamable-http
# mcp dev AI_AGENTS\weather_server.py
if __name__ == "__main__":
    mcp.run("streamable-http", port=8002)
