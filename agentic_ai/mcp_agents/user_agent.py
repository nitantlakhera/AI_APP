import json

from agentic_ai.agents.llm_provider import chat_llm_tools


# ============================================================
# USER AGENT
# ============================================================

async def user_agent(question, mcp_manager):
    print("\n========================================")
    print("USER AGENT")
    print("========================================")

    # ========================================================
    # GET USER MCP TOOLS
    # ========================================================

    tools = mcp_manager.get_tools_for_server("postgres")

    print("Received Tools:", tools)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful user information assistant. "
                "When the user asks for information about a user, "
                "use the available user database tool. "
                "Do not invent user information."
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

        print("\n========================================")
        print("CALLING LLM")
        print("========================================")

        response = chat_llm_tools(
            messages,
            tools
        )

        message = response.choices[0].message

        # ====================================================
        # NO TOOL CALL
        # ====================================================

        if not message.tool_calls:
            return message.content

        # ====================================================
        # TOOL CALL
        # ====================================================

        messages.append(message)

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            print("\n========================================")
            print("TOOL CALL")
            print("========================================")

            print("Tool:", tool_name)
            print("Arguments:", arguments)

            # =================================================
            # CALL MCP TOOL
            # =================================================

            result = await mcp_manager.call_mcp_tool(
                tool_name,
                arguments
            )

            print("\nMCP RESULT:")
            print(result)

            # =================================================
            # SEND RESULT BACK TO LLM
            # =================================================

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                }
            )

        continue
