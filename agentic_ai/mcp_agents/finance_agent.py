import json
from agentic_ai.agents.llm_provider import chat_llm_tools


# ============================================================
# FINANCE AGENT
# ============================================================

async def finance_agent(question, mcp_manager):
    print("\n========================================")
    print("FINANCE AGENT")
    print("========================================")

    # ========================================================
    # GET FINANCE MCP TOOLS
    # ========================================================

    tools = mcp_manager.get_tools_for_server("finance")

    print("Received Tools:", tools)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a Finance Agent. "
                "Use the available finance tool for currency questions. "
                "Do not invent exchange rates."
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

        assistant_message = response.choices[0].message

        # ====================================================
        # NO TOOL CALL
        # ====================================================

        if not assistant_message.tool_calls:
            return assistant_message.content

        # ====================================================
        # TOOL CALL
        # ====================================================

        messages.append(assistant_message)

        for tool_call in assistant_message.tool_calls:
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

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

        continue
