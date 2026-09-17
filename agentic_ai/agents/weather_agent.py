from agentic_ai.agents.llm_provider import chat_llm_tools
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


# ============================================================
# REAL WEATHER TOOL
# ============================================================

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


# ============================================================
# WEATHER AGENT
# ============================================================

def weather_agent(question):
    print("\n========================================")
    print("WEATHER AGENT")
    print("========================================")

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather information for a city.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string"
                        }
                    },
                    "required": ["city"]
                }
            }
        }
    ]

    messages = [
        {
            "role": "system",
            "content": (
                "You are a weather assistant. "
                "Use the weather tool when necessary. "
                "After receiving weather data, answer the user's question "
                "in natural, conversational plain English. "
                "Do not expose tool calls, JSON, or raw tool output."
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]

    # ========================================================
    # AGENT LOOP
    # ========================================================

    while True:

        response = chat_llm_tools(messages, tools)

        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:

            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:

                tool_name = tool_call.function.name

                arguments = json.loads(
                    tool_call.function.arguments
                )

                if tool_name == "get_weather":

                    city = arguments["city"]
                    result = get_weather(city)

                else:

                    result = {
                        "error": f"Unknown tool: {tool_name}"
                    }

                # ============================================
                # SEND TOOL RESULT BACK TO LLM
                # ============================================

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

            continue

        # ====================================================
        # NO TOOL CALL -> FINAL ANSWER
        # ====================================================
        return assistant_message.content


if __name__ == "__main__":
    response = weather_agent("what is the weather of Bangalore?")
    print("Agent Response: ", response)
