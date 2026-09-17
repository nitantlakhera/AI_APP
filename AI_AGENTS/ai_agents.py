import json

import requests
from openai import OpenAI


# ============================================================
# 1. TOOL IMPLEMENTATIONS
# ============================================================

# def get_weather(city: str):
#     """
#     Get weather information for a city.
#     """
#
#     weather_data = {
#         "Bangalore": {
#             "temperature": 25,
#             "condition": "Cloudy"
#         },
#         "Delhi": {
#             "temperature": 32,
#             "condition": "Sunny"
#         },
#         "Mumbai": {
#             "temperature": 29,
#             "condition": "Rainy"
#         }
#     }
#
#     return weather_data.get(
#         city,
#         {
#             "temperature": "unknown",
#             "condition": "unknown"
#         }
#     )


def get_weather(city: str):
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


def get_user_info(user_id: int):
    """
    Get information about a user using user ID.
    """

    users = {
        101: {
            "name": "Rahul",
            "city": "Bangalore",
            "role": "Software Engineer"
        },
        102: {
            "name": "Amit",
            "city": "Delhi",
            "role": "Manager"
        }
    }

    return users.get(
        user_id,
        {
            "error": "User not found"
        }
    )


# ============================================================
# 2. TOOL DEFINITIONS / SCHEMAS
# ============================================================

tools = [

    # --------------------------------------------------------
    # WEATHER TOOL
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "get_weather",

            "description": (
                "Get weather information for a city. "
                "Use ONLY when the user asks about weather, "
                "temperature, rain, sunny, cloudy, or weather "
                "conditions for a specific city."
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city"
                    }
                },

                "required": ["city"]
            }
        }
    },

    # --------------------------------------------------------
    # USER INFORMATION TOOL
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "get_user_info",

            "description": (
                "Get information about a user using their user ID. "
                "Use ONLY when the user asks about a specific "
                "user ID, such as the user's name, city, or role."
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "Unique ID of the user"
                    }
                },

                "required": ["user_id"]
            }
        }
    }
]

# ============================================================
# 3. TOOL REGISTRY
# ============================================================

available_tools = {
    "get_weather": get_weather,
    "get_user_info": get_user_info
}

# ============================================================
# 4. OLLAMA CLIENT
# ============================================================

client = OpenAI(
    base_url="http://localhost:11434/v1/",
    api_key="ollama"
)


# ============================================================
# 5. AGENT
# ============================================================

def run_agent(user_question):
    messages = [

        # ----------------------------------------------------
        # SYSTEM MESSAGE
        # ----------------------------------------------------

        {
            "role": "system",
            "content": """
You are a helpful AI assistant.

You have access to the following tools:

1. get_weather
   - Use ONLY when the user explicitly asks about:
     weather, temperature, rain, sunny, cloudy,
     or weather conditions for a city.

2. get_user_info
   - Use ONLY when the user asks for information
     about a specific user ID.

IMPORTANT RULES:

- If the user asks a general knowledge question,
  answer directly without using a tool.

- Do NOT call get_weather for general questions.

- Do NOT call get_user_info for general questions.

- Never invent a city.

- Never invent a user ID.

- Never call a tool simply because the tool is available.

- If no tool is required, do not generate a tool call.

Examples:

User: What is Java?
Action: Answer directly. Do NOT call a tool.

User: Explain Python.
Action: Answer directly. Do NOT call a tool.

User: What is the weather in Bangalore?
Action: Call get_weather with city="Bangalore".

User: Is it raining in Mumbai?
Action: Call get_weather with city="Mumbai".

User: Tell me the details of user 101.
Action: Call get_user_info with user_id=101.
""".strip()
        },

        # ----------------------------------------------------
        # USER MESSAGE
        # ----------------------------------------------------

        {
            "role": "user",
            "content": user_question
        }
    ]

    # ========================================================
    # PRINT USER QUESTION
    # ========================================================

    print("\n========================================")
    print("USER QUESTION")
    print("========================================")
    print(user_question)

    # ========================================================
    # AGENT LOOP
    # ========================================================

    while True:

        print("\n========================================")
        print("CALLING LLM")
        print("========================================")

        # ----------------------------------------------------
        # CALL LLM
        # ----------------------------------------------------

        response = client.chat.completions.create(

            model="qwen2.5:3b",

            messages=messages,

            tools=tools,

            # Let the LLM decide whether to use a tool
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # ----------------------------------------------------
        # PRINT TOOL CALLS
        # ----------------------------------------------------

        print("\nAssistant tool calls:")
        print(assistant_message.tool_calls)

        # ====================================================
        # CASE 1: LLM DECIDED TO USE TOOL
        # ====================================================

        if assistant_message.tool_calls:

            # Add assistant tool-call message
            messages.append(assistant_message)

            # ------------------------------------------------
            # Execute every tool requested by the LLM
            # ------------------------------------------------

            for tool_call in assistant_message.tool_calls:

                tool_name = tool_call.function.name

                arguments = json.loads(
                    tool_call.function.arguments
                )

                print("\n----------------------------------------")
                print("LLM DECIDED TO CALL TOOL")
                print("----------------------------------------")

                print("Tool:", tool_name)
                print("Arguments:", arguments)

                # ------------------------------------------------
                # Find Python function from registry
                # ------------------------------------------------

                function = available_tools.get(tool_name)

                if function is None:

                    result = {
                        "error": f"Unknown tool: {tool_name}"
                    }

                else:

                    try:

                        # Execute actual Python function
                        result = function(**arguments)

                    except Exception as e:

                        result = {
                            "error": str(e)
                        }

                # ------------------------------------------------
                # Print tool result
                # ------------------------------------------------

                print("Tool Result:", result)

                # ------------------------------------------------
                # Send result back to LLM
                # ------------------------------------------------

                messages.append(
                    {
                        "role": "tool",

                        "tool_call_id": tool_call.id,

                        "content": json.dumps(result)
                    }
                )

            # ------------------------------------------------
            # Continue agent loop
            # LLM will now process the tool result
            # ------------------------------------------------

            continue

        # ====================================================
        # CASE 2: NO TOOL REQUIRED
        # ====================================================

        print("\n========================================")
        print("FINAL ANSWER")
        print("========================================")

        print(assistant_message.content)

        break


# ============================================================
# 6. TEST
# ============================================================

if __name__ == "__main__":
    # run_agent(
    #     "What is Java language in programming?"
    # )

    run_agent("What is the weather in Bhopal?")

    # run_agent("What is the name and role of user 101?")
