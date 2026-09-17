import asyncio
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from mcp import Client

# ============================================================
# Ollama LLM
# ============================================================

llm = OpenAI(
    base_url="http://localhost:11434/v1/",
    api_key="ollama"
)

MODEL_NAME = "qwen2.5:3b"

# ============================================================
# MCP SERVERS
# ============================================================

MCP_SERVERS = {
    "weather": "http://localhost:8002/mcp"
    # "finance": "http://localhost:8001/mcp"
}

# ============================================================
# TOOL REGISTRY
#
# This will be populated automatically from MCP servers.
# ============================================================

tool_registry = {}


# ============================================================
# Convert MCP tool → OpenAI tool definition
# ============================================================

def mcp_tool_to_openai_tool(server_name, mcp_tool):
    tool_name = mcp_tool.name

    description = mcp_tool.description or (
        f"Tool provided by {server_name} MCP server"
    )

    # MCP input schema is already JSON Schema
    input_schema = mcp_tool.input_schema

    openai_tool = {
        "type": "function",
        "function": {
            "name": tool_name,
            "description": description,
            "parameters": input_schema
        }
    }

    # Remember where this tool came from
    tool_registry[tool_name] = {
        "server": server_name,
        "url": MCP_SERVERS[server_name]
    }

    return openai_tool


# ============================================================
# DISCOVER MCP TOOLS
# ============================================================

async def discover_tools():
    print("\n========================================")
    print("DISCOVERING MCP TOOLS")
    print("========================================")

    all_tools = []

    for server_name, server_url in MCP_SERVERS.items():

        print(f"\nConnecting to: {server_name}")
        print(f"URL: {server_url}")

        async with Client(server_url) as mcp_client:

            response = await mcp_client.list_tools()

            print(f"\nTools from {server_name} MCP:")

            for mcp_tool in response.tools:
                print(f"  - {mcp_tool.name}")

                openai_tool = mcp_tool_to_openai_tool(
                    server_name,
                    mcp_tool
                )

                all_tools.append(openai_tool)

    print("\n========================================")
    print("DISCOVERED TOOLS")
    print("========================================")

    for tool in all_tools:
        print(
            " -",
            tool["function"]["name"]
        )

    return all_tools


# ============================================================
# CALL MCP TOOL
# ============================================================

async def call_mcp_tool(
        tool_name,
        arguments
):
    if tool_name not in tool_registry:
        return {
            "error": f"Tool '{tool_name}' not found"
        }

    tool_info = tool_registry[tool_name]

    server_name = tool_info["server"]
    server_url = tool_info["url"]

    print("\n========================================")
    print("MCP TOOL EXECUTION")
    print("========================================")

    print("Tool:", tool_name)
    print("Server:", server_name)
    print("Arguments:", arguments)

    async with Client(server_url) as mcp_client:

        result = await mcp_client.call_tool(
            tool_name,
            arguments
        )

        print("\nMCP RESULT:")
        print(result)

        if result.structured_content:
            return result.structured_content

        return {
            "content": str(result.content)
        }


# ============================================================
# AGENT
# ============================================================

async def run_agent(question):
    print("\n========================================")
    print("USER QUESTION")
    print("========================================")

    print(question)

    # --------------------------------------------------------
    # Discover tools dynamically
    # --------------------------------------------------------

    tools = await discover_tools()

    # # Get only weather tools
    # tools = m.get_tools_for_server(
    #     "weather"
    # )

    # --------------------------------------------------------
    # Messages
    # --------------------------------------------------------

    messages = [

        {
            "role": "system",

            "content": """
You are a helpful AI assistant.

You have access to tools provided by MCP servers.

Choose the appropriate tool when the user's question
requires external information.

Do not invent information that should come from a tool.

For normal questions that do not require a tool,
answer directly.
"""
        },

        {
            "role": "user",
            "content": question
        }

    ]

    # --------------------------------------------------------
    # Agent loop
    # --------------------------------------------------------

    while True:

        print("\n========================================")
        print("CALLING LLM")
        print("========================================")

        response = llm.chat.completions.create(

            model=MODEL_NAME,

            messages=messages,

            tools=tools,

            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # ----------------------------------------------------
        # LLM requested a tool
        # ----------------------------------------------------

        if assistant_message.tool_calls:

            print("\n========================================")
            print("LLM REQUESTED TOOL")
            print("========================================")

            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:

                tool_name = tool_call.function.name

                arguments = json.loads(
                    tool_call.function.arguments
                )

                print("\nTool:")
                print(tool_name)

                print("\nArguments:")
                print(arguments)

                # --------------------------------------------
                # Call MCP dynamically
                # --------------------------------------------

                try:

                    result = await call_mcp_tool(
                        tool_name,
                        arguments
                    )

                except Exception as e:

                    result = {
                        "error": str(e)
                    }

                # --------------------------------------------
                # Send result back to LLM
                # --------------------------------------------

                messages.append({

                    "role": "tool",

                    "tool_call_id": tool_call.id,

                    "content": json.dumps(result)
                })

            # Continue agent loop
            continue

        # ----------------------------------------------------
        # Final answer
        # ----------------------------------------------------

        print("\n========================================")
        print("FINAL ANSWER")
        print("========================================")

        print(assistant_message.content)

        break


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    asyncio.run(
        run_agent(
            "What is the weather in Bangalore?"
        )
    )
