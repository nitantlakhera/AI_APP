import asyncio
import json

from agentic_ai.agents.llm_provider import chat_llm_tools
from agentic_ai.mcp_agents.MCPManager import MCPManager


# ============================================================
# WEATHER AGENT
# ============================================================

async def weather_agent(question, mcp_manager):
    print("\n========================================")
    print("WEATHER AGENT")
    print("========================================")

    # --------------------------------------------------------
    # Get only weather tools
    # --------------------------------------------------------

    tools = mcp_manager.get_tools_for_server(
        "weather"
    )

    print("Received Tools:", tools)

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

        response = chat_llm_tools(
            messages,
            tools
        )

        assistant_message = response.choices[0].message

        # ====================================================
        # LLM WANTS TO CALL TOOL
        # ====================================================

        if assistant_message.tool_calls:

            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name

                arguments = json.loads(
                    tool_call.function.arguments
                )

                print("\nTool:", tool_name)
                print("Arguments:", arguments)

                # ------------------------------------------------
                # MCP Manager handles MCP communication
                # ------------------------------------------------

                result = await mcp_manager.call_mcp_tool(
                    tool_name,
                    arguments
                )

                print("Tool Result:", result)

                # ------------------------------------------------
                # Send result back to LLM
                # ------------------------------------------------

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


# ============================================================
# MAIN
# ============================================================

async def main():
    # Create central MCP manager
    mcp_manager = MCPManager()

    # Discover all MCP tools
    await mcp_manager.discover_tools()

    # Run weather agent
    result = await weather_agent(
        "What is the weather in Bangalore?",
        mcp_manager
    )

    print("\n========================================")
    print("FINAL ANSWER")
    print("========================================")

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
