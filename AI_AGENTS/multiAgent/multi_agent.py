import json
from openai import OpenAI

# ============================================================
# OLLAMA
# ============================================================

llm = OpenAI(
    base_url="http://localhost:11434/v1/",
    api_key="ollama"
)

MODEL_NAME = "qwen2.5:3b"


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
                "You are a Weather Agent. "
                "Use get_weather when weather information is required."
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]

    while True:

        response = llm.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

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

                    weather_data = {
                        "Bangalore": {
                            "temperature": 25,
                            "condition": "Cloudy"
                        },
                        "Delhi": {
                            "temperature": 32,
                            "condition": "Sunny"
                        },
                        "Mumbai": {
                            "temperature": 29,
                            "condition": "Rainy"
                        }
                    }

                    result = weather_data.get(
                        city,
                        {
                            "error": f"Weather not available for {city}"
                        }
                    )

                else:

                    result = {
                        "error": f"Unknown tool: {tool_name}"
                    }

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

            continue

        return assistant_message.content


# ============================================================
# FINANCE AGENT
# ============================================================

def finance_agent(question):
    print("\n========================================")
    print("FINANCE AGENT")
    print("========================================")

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_exchange_rate",
                "description": (
                    "Get exchange rate between two currencies."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "from_currency": {
                            "type": "string"
                        },
                        "to_currency": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "from_currency",
                        "to_currency"
                    ]
                }
            }
        }
    ]

    messages = [
        {
            "role": "system",
            "content": (
                "You are a Finance Agent. "
                "Use get_exchange_rate for currency questions."
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]

    while True:

        response = llm.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:

            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:

                tool_name = tool_call.function.name

                arguments = json.loads(
                    tool_call.function.arguments
                )

                if tool_name == "get_exchange_rate":

                    rates = {
                        "USD_INR": 88.0,
                        "EUR_INR": 103.0,
                        "GBP_INR": 119.0,
                        "INR_USD": 0.0114,
                        "INR_EUR": 0.0097,
                        "INR_GBP": 0.0084
                    }

                    key = (
                        f"{arguments['from_currency'].upper()}_"
                        f"{arguments['to_currency'].upper()}"
                    )

                    result = {
                        "rate": rates.get(
                            key,
                            "Rate not available"
                        )
                    }

                else:

                    result = {
                        "error": f"Unknown tool: {tool_name}"
                    }

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

            continue

        return assistant_message.content


# ============================================================
# USER AGENT
# ============================================================

def user_agent(question):
    print("\n========================================")
    print("USER AGENT")
    print("========================================")

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

    # For this first version we let the LLM extract the ID.
    response = llm.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract the user ID from the question. "
                    "Return ONLY the integer user ID."
                )
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )

    user_id = int(response.choices[0].message.content.strip())

    return users.get(
        user_id,
        {"error": f"User {user_id} not found"}
    )


# ============================================================
# SUPERVISOR AGENT
# ============================================================

def supervisor_agent(question):
    print("\n========================================")
    print("SUPERVISOR AGENT")
    print("========================================")

    response = llm.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": """
You are a Supervisor Agent.

You manage three specialized agents:

1. weather
   Handles weather and temperature questions.

2. finance
   Handles currency and exchange-rate questions.

3. user
   Handles questions about users.

Return ONLY one word:

weather
finance
user
"""
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )

    decision = response.choices[0].message.content.strip().lower()

    print("\nSupervisor decision:", decision)

    return decision


# ============================================================
# MULTI-AGENT ORCHESTRATOR
# ============================================================

def run_multi_agent(question):
    print("\n")
    print("========================================")
    print("MULTI-AGENT SYSTEM")
    print("========================================")

    print("\nUser:")
    print(question)

    # --------------------------------------------------------
    # Step 1: Supervisor decides
    # --------------------------------------------------------

    agent_name = supervisor_agent(question)

    # --------------------------------------------------------
    # Step 2: Call specialized agent
    # --------------------------------------------------------

    if agent_name == "weather":

        result = weather_agent(question)

    elif agent_name == "finance":

        result = finance_agent(question)

    elif agent_name == "user":

        result = user_agent(question)

    else:

        result = (
            "Supervisor could not determine "
            "the appropriate agent."
        )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    print("\n========================================")
    print("FINAL ANSWER")
    print("========================================")

    print(result)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    run_multi_agent(
        "What is the weather in Bangalore?"
    )
