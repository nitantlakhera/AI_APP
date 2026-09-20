import json

from agentic_ai.agents.llm_provider import chat_llm

from agentic_ai.mcp_agents.weather_agent import weather_agent
from agentic_ai.mcp_agents.finance_agent import finance_agent
from agentic_ai.mcp_agents.user_agent import user_agent

from agentic_ai.a2a.a2a_client import send_to_recommendation_agent


# ============================================================
# SUPERVISOR AGENT
# ============================================================


async def run_supervisor_agent(question, mcp_manager):

    print("\n========================================")
    print("SUPERVISOR AGENT")
    print("========================================")

    # ========================================================
    # 1. ASK SUPERVISOR LLM WHICH AGENTS ARE REQUIRED
    # ========================================================

    messages = [
        {
            "role": "system",
            "content": """
You are a Supervisor Agent.

You manage three specialized agents:

1. weather
   Handles weather, temperature, rain and weather conditions.

2. finance
   Handles currency, exchange rates, budget and financial information.

3. user
   Handles questions about users, user profiles, names, cities and roles.

Determine which agents are required to answer the user's question.

For a personalized recommendation that needs user,
weather and financial information, select all three agents.

Return ONLY valid JSON.

Examples:

{"agents": ["weather"]}

{"agents": ["finance"]}

{"agents": ["user"]}

{"agents": ["weather", "finance"]}

{"agents": ["weather", "finance", "user"]}

Do not return any explanation.
"""
        },
        {
            "role": "user",
            "content": question
        }
    ]

    response = chat_llm(messages)

    decision = response.choices[0].message.content.strip()

    print("\nSupervisor decision:")
    print(decision)

    # ========================================================
    # 2. PARSE SUPERVISOR DECISION
    # ========================================================

    try:

        result = json.loads(decision)

        agents = result.get("agents", [])

    except json.JSONDecodeError:

        print("\nInvalid supervisor response")

        return "Unable to understand the request."

    print("\nSelected agents:")
    print(agents)

    # ========================================================
    # 3. CALL SPECIALIZED AGENTS
    # ========================================================

    weather_result = "No weather information requested."
    finance_result = "No finance information requested."
    user_result = "No user information requested."

    # --------------------------------------------------------
    # WEATHER AGENT
    # --------------------------------------------------------

    if "weather" in agents:

        print("\n========================================")
        print("CALLING WEATHER AGENT")
        print("========================================")

        weather_result = await weather_agent(
            question,
            mcp_manager
        )

    # --------------------------------------------------------
    # FINANCE AGENT
    # --------------------------------------------------------

    if "finance" in agents:

        print("\n========================================")
        print("CALLING FINANCE AGENT")
        print("========================================")

        finance_result = await finance_agent(
            question,
            mcp_manager
        )

    # --------------------------------------------------------
    # USER AGENT
    # --------------------------------------------------------

    if "user" in agents:

        print("\n========================================")
        print("CALLING USER AGENT")
        print("========================================")

        user_result = await user_agent(
            question,
            mcp_manager
        )

    # ========================================================
    # 4. DISPLAY SPECIALIZED AGENT RESULTS
    # ========================================================

    print("\n========================================")
    print("SPECIALIZED AGENT RESULTS")
    print("========================================")

    print("\nWEATHER RESULT:")
    print(weather_result)

    print("\nFINANCE RESULT:")
    print(finance_result)

    print("\nUSER RESULT:")
    print(user_result)

    # ========================================================
    # 5. COMBINE ALL RESULTS
    # ========================================================

    combined_result = f"""
USER QUESTION:
{question}

USER AGENT RESULT:
{user_result}

WEATHER AGENT RESULT:
{weather_result}

FINANCE AGENT RESULT:
{finance_result}
"""

    print("\n========================================")
    print("COMBINED AGENT RESULTS")
    print("========================================")

    print(combined_result)

    # ========================================================
    # 6. CALL RECOMMENDATION AGENT THROUGH A2A
    # ========================================================

    print("\n========================================")
    print("CALLING RECOMMENDATION AGENT THROUGH A2A")
    print("========================================")

    recommendation = await send_to_recommendation_agent(
        combined_result
    )

    # ========================================================
    # 7. FINAL RESULT
    # ========================================================

    print("\n========================================")
    print("FINAL RECOMMENDATION")
    print("========================================")

    print(recommendation)

    return recommendation