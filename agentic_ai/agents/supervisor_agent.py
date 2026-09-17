from agentic_ai.agents.llm_provider import chat_llm


# ============================================================
# SUPERVISOR AGENT
# ============================================================


def run_supervisor_agent(question):
    print("\n========================================")
    print("SUPERVISOR AGENT")
    print("========================================")

    messages = [
        {
            "role": "system",
            "content": """
    You are a Supervisor Agent.

    You manage three specialized agents:

    1. weather
       Handles weather and temperature questions.

    2. finance
       Handles currency and exchange-rate questions.

    3. user
       Handles questions about users.

    Return ONLY one word:

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

    # Get LLM response
    response = chat_llm(messages)

    decision = response.choices[0].message.content.strip().lower()

    print("\nSupervisor decision:", decision)

    return decision
