import asyncio
import json
from openai import OpenAI
from mcp import Client


# ============================================================
# 1. TOOL IMPLEMENTATIONS
# ============================================================

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
# 2. MCP SERVER URL
# ============================================================

MCP_SERVER_URL = "http://localhost:8000/mcp"

# ============================================================
# 3. TOOL DEFINITIONS / SCHEMAS
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

    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "Get the exchange rate between two currencies. Use this for currency conversion or exchange rate questions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_currency": {
                        "type": "string",
                        "description": "Source currency, for example USD"
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "Target currency, for example INR"
                    }
                },
                "required": ["from_currency", "to_currency"]
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
# 4. TOOL REGISTRY
# ============================================================
# Only for get user info since no mcp server is there for this.
available_tools = {
    # "get_weather": get_weather,  # will be invoked via MCP
    "get_user_info": get_user_info
}

# ============================================================
# 5. OLLAMA CLIENT
# ============================================================

client = OpenAI(
    base_url="http://localhost:11434/v1/",
    api_key="ollama"
)


# ============================================================
# 6. CALL MCP TOOL
# ============================================================

async def call_mcp_tool(tool_name, arguments):
    print("\n========================================")
    print("MCP CLIENT")
    print("========================================")

    print("Connecting to:", MCP_SERVER_URL)
    print("Tool:", tool_name)
    print("Arguments:", arguments)

    async with Client(MCP_SERVER_URL) as mcp_client:
        result = await mcp_client.call_tool(
            tool_name,
            arguments
        )

        print("\nMCP SERVER RESULT:")
        print(result)

        if result.structured_content:
            return result.structured_content

        return {
            "content": str(result.content)
        }


# ============================================================
# 7. AGENT
# ============================================================

async def run_agent(user_question):
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
   - This tool is provided through an MCP server.
   - Use ONLY when the user asks about:
     weather, temperature, rain, sunny, cloudy,
     or weather conditions for a city.

2. get_user_info
   - This is a normal Python application tool.
   - Use ONLY when the user asks about a specific user ID.

IMPORTANT RULES:

- If the user asks a general knowledge question,
  answer directly.

- Do NOT call get_weather for general questions.

- Do NOT call get_user_info for general questions.

- Never invent a city.

- Never invent a user ID.

- Never call a tool simply because it is available.

Examples:

User: What is Java?
Action: Answer directly.

User: Explain Python.
Action: Answer directly.

User: What is the weather in Bangalore?
Action: Call get_weather.

User: Is it raining in Mumbai?
Action: Call get_weather.

User: Tell me the details of user 101.
Action: Call get_user_info.
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
    # AGENT LOOP
    # ========================================================

    while True:

        print("\n========================================")
        print("CALLING LLM")
        print("========================================")

        response = client.chat.completions.create(

            model="qwen2.5:3b",

            messages=messages,

            tools=tools,

            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        print("\nASSISTANT TOOL CALLS:")
        print(assistant_message.tool_calls)

        # ====================================================
        # LLM WANTS TO USE TOOL
        # ====================================================

        if assistant_message.tool_calls:

            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:

                tool_name = tool_call.function.name

                arguments = json.loads(
                    tool_call.function.arguments
                )

                print("\n========================================")
                print("LLM DECIDED TO CALL TOOL")
                print("========================================")

                print("Tool:", tool_name)
                print("Arguments:", arguments)

                # =================================================
                # MCP TOOLS
                # =================================================

                if tool_name in [
                    "get_weather",
                    "get_exchange_rate"
                ]:

                    try:

                        result = await call_mcp_tool(
                            tool_name,
                            arguments
                        )

                    except Exception as e:

                        result = {
                            "error": str(e)
                        }

                # =================================================
                # USER INFO → NORMAL PYTHON
                # =================================================

                elif tool_name == "get_user_info":

                    function = available_tools.get(
                        tool_name
                    )

                    if function is None:

                        result = {
                            "error": f"Unknown tool: {tool_name}"
                        }

                    else:

                        try:

                            result = function(**arguments)

                        except Exception as e:

                            result = {
                                "error": str(e)
                            }

                else:

                    result = {
                        "error": f"Unknown tool: {tool_name}"
                    }

                # ------------------------------------------------
                # PRINT RESULT
                # ------------------------------------------------

                print("\nTOOL RESULT:")
                print(result)

                # ------------------------------------------------
                # SEND RESULT BACK TO LLM
                # ------------------------------------------------

                messages.append(
                    {
                        "role": "tool",

                        "tool_call_id": tool_call.id,

                        "content": json.dumps(result)
                    }
                )

            # ------------------------------------------------
            # Continue loop
            # ------------------------------------------------

            continue

        # ====================================================
        # NO TOOL
        # ====================================================

        print("\n========================================")
        print("FINAL ANSWER")
        print("========================================")

        print(assistant_message.content)

        break


# ============================================================
# 8. TEST
# ============================================================

if __name__ == "__main__":
    # asyncio.run(
    #     run_agent(
    #         "What is the weather in Bangalore?"
    #     )
    # )

    # asyncio.run(
    #     run_agent("What is the name and role of user 101?")
    # )

    asyncio.run(
        run_agent("What is the exchange rate from USD to INR?")
    )
