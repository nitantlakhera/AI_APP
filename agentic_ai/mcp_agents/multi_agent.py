import asyncio

from agentic_ai.mcp_agents.MCPManager import MCPManager
from agentic_ai.mcp_agents.supervisor_agent import run_supervisor_agent
from agentic_ai.mcp_agents.weather_agent import weather_agent
from agentic_ai.mcp_agents.finance_agent import finance_agent
from agentic_ai.mcp_agents.user_agent import user_agent


# ============================================================
# MULTI-AGENT ORCHESTRATOR
# ============================================================

async def run_multi_agent(question):

    print("\n")
    print("========================================")
    print("MULTI-AGENT SYSTEM")
    print("========================================")

    print("\nUser:")
    print(question)

    # ========================================================
    # CREATE CENTRAL MCP MANAGER
    # ========================================================

    mcp_manager = MCPManager()

    # ========================================================
    # DISCOVER ALL MCP TOOLS
    # ========================================================

    await mcp_manager.discover_tools()

    # ========================================================
    # STEP 1: SUPERVISOR DECIDES
    # ========================================================

    agent_name = run_supervisor_agent(question)

    # ========================================================
    # STEP 2: CALL SPECIALIZED AGENT
    # ========================================================

    if agent_name == "weather":

        result = await weather_agent(
            question,
            mcp_manager
        )

    elif agent_name == "finance":

        result = await finance_agent(
            question,
            mcp_manager
        )

    elif agent_name == "user":

        result = await user_agent(
            question,
            mcp_manager
        )

    else:

        result = (
            "Supervisor could not determine "
            "the appropriate agent."
        )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print("\n========================================")
    print("FINAL ANSWER")
    print("========================================")

    print(result)

    return result


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    asyncio.run(
        run_multi_agent(
            "Weather of Jabalpur?"
        )
    )