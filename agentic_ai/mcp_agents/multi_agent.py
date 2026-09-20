import asyncio

from agentic_ai.mcp_agents.MCPManager import MCPManager
from agentic_ai.mcp_agents.supervisor_agent import run_supervisor_agent


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
    # SUPERVISOR
    #
    # Supervisor will:
    #
    # 1. Decide required agents
    # 2. Call Weather Agent
    # 3. Call Finance Agent
    # 4. Call User Agent
    # 5. Collect their results
    # 6. Call Recommendation Agent through A2A
    # 7. Return final recommendation
    # ========================================================

    result = await run_supervisor_agent(
        question,
        mcp_manager
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
            "Based on my user profile, current weather "
            "and finances, what should I do today?"
        )
    )
