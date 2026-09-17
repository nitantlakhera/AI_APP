from agentic_ai.agents.supervisor_agent import run_supervisor_agent
from agentic_ai.agents.weather_agent import weather_agent
from agentic_ai.agents.finance_agent import finance_agent
from agentic_ai.agents.user_agent import user_agent


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

    agent_name = run_supervisor_agent(question)

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

    # print("LLM Response: ", result)

    return result


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    run_multi_agent(
        "What is the weather in Bangalore?"
    )
