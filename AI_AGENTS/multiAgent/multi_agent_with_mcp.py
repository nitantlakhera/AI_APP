import asyncio
import json

from openai import OpenAI
from mcp import Client

# ============================================================
# OLLAMA
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
    "weather": "http://localhost:8000/mcp",
    "finance": "http://localhost:8002/mcp",
    "user": "http://localhost:8003/mcp"
}

# ============================================================
# MCP TOOL REGISTRY
# ============================================================

tool_registry = {}


# ============================================================
# DISCOVER TOOLS
# ============================================================

async def discover_tools():
    print("\n========================================")
    print("DISCOVERING MCP TOOLS")
    print("========================================")

    all_tools = []

    for server_name, server_url in MCP_SERVERS.items():

        print(f"\nConnecting to {server_name}")
        print(server_url)

        async with Client(server_url) as mcp_client:

            response = await mcp_client.list_tools()

            for mcp_tool in response.tools:
                print(
                    f"  {server_name} → "
                    f"{mcp_tool.name}"
                )

                # IMPORTANT:
                # Make tool names globally unique.
                openai_tool_name = (
                    f"{server_name}__{mcp_tool.name}"
                )

                tool_registry[openai_tool_name] = {
                    "server": server_name,
                    "url": server_url,
                    "mcp_tool_name": mcp_tool.name
                }

                all_tools.append({
                    "type": "function",
                    "function": {
                        "name": openai_tool_name,
                        "description": (
                                mcp_tool.description
                                or
                                f"Tool from {server_name} MCP"
                        ),
                        "parameters": mcp_tool.input_schema
                    }
                })

    return all_tools


# ============================================================
# CALL MCP TOOL
# ============================================================

async def call_mcp_tool(
        tool_name,
        arguments
):
    print("\n========================================")
    print("CALLING MCP TOOL")
    print("========================================")

    tool_info = tool_registry.get(tool_name)

    if tool_info is None:
        return {
            "error": f"Unknown tool: {tool_name}"
        }

    server_name = tool_info["server"]
    server_url = tool_info["url"]
    mcp_tool_name = tool_info["mcp_tool_name"]

    print("Server:", server_name)
    print("Tool:", mcp_tool_name)
    print("Arguments:", arguments)

    async with Client(server_url) as mcp_client:

        result = await mcp_client.call_tool(
            mcp_tool_name,
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
# SPECIALIZED AGENT
# ============================================================

async def specialist_agent(
        agent_name,
        question,
        tools
):
    print("\n========================================")
    print(f"{agent_name.upper()} AGENT")
    print("========================================")

    messages = [
        {
            "role": "system",
            "content": f"""
You are the {agent_name} specialist agent.

You have access to MCP tools.

Use the available tool when required.

Do not invent information.

Return a clear answer based on the tool result.
"""
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

        # ----------------------------------------------------
        # Tool requested
        # ----------------------------------------------------

        if assistant_message.tool_calls:

            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name

                arguments = json.loads(
                    tool_call.function.arguments
                )

                result = await call_mcp_tool(
                    tool_name,
                    arguments
                )

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

            continue

        return assistant_message.content


# ============================================================
# SUPERVISOR
# ============================================================

async def supervisor_agent(
        question,
        tools
):
    print("\n========================================")
    print("SUPERVISOR AGENT")
    print("========================================")

    messages = [
        {
            "role": "system",
            "content": """
You are the Supervisor Agent.

You coordinate three specialist agents:

WEATHER AGENT
- Handles weather questions.

FINANCE AGENT
- Handles currency and exchange-rate questions.

USER AGENT
- Handles questions about users.

Decide which specialist should handle the request.

Return ONLY one of:

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

    response = llm.chat.completions.create(
        model=MODEL_NAME,
        messages=messages
    )

    decision = (
        response
        .choices[0]
        .message
        .content
        .strip()
        .lower()
    )

    print("\nSupervisor decision:", decision)

    return decision


# ============================================================
# MULTI-AGENT ORCHESTRATOR
# ============================================================

async def run_multi_agent(question):
    print("\n")
    print("========================================")
    print("MULTI-AGENT MCP SYSTEM")
    print("========================================")

    print("\nUSER:")
    print(question)

    # --------------------------------------------------------
    # Discover MCP tools
    # --------------------------------------------------------

    tools = await discover_tools()

    print("\n========================================")
    print("DISCOVERED TOOLS")
    print("========================================")

    for tool in tools:
        print(
            " -",
            tool["function"]["name"]
        )

    # --------------------------------------------------------
    # Supervisor
    # --------------------------------------------------------

    selected_agent = await supervisor_agent(
        question,
        tools
    )

    # --------------------------------------------------------
    # Select specialist tools
    # --------------------------------------------------------

    if selected_agent == "weather":

        specialist_tools = [
            tool
            for tool in tools
            if tool["function"]["name"].startswith(
                "weather__"
            )
        ]

    elif selected_agent == "finance":

        specialist_tools = [
            tool
            for tool in tools
            if tool["function"]["name"].startswith(
                "finance__"
            )
        ]

    elif selected_agent == "user":

        specialist_tools = [
            tool
            for tool in tools
            if tool["function"]["name"].startswith(
                "user__"
            )
        ]

    else:

        print("Unknown agent selected.")

        return

    # --------------------------------------------------------
    # Call specialist agent
    # --------------------------------------------------------

    answer = await specialist_agent(
        selected_agent,
        question,
        specialist_tools
    )

    # --------------------------------------------------------
    # Final answer
    # --------------------------------------------------------

    print("\n========================================")
    print("FINAL ANSWER")
    print("========================================")

    print(answer)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    asyncio.run(
        run_multi_agent(
            "What is the weather in Bangalore?"
        )
    )
