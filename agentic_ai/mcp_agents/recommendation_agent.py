from agentic_ai.agents.llm_provider import chat_llm


def recommendation_agent(
        user_result,
        weather_result,
        finance_result
):
    print("\n========================================")
    print("RECOMMENDATION AGENT")
    print("========================================")

    print("\nUser Result:")
    print(user_result)

    print("\nWeather Result:")
    print(weather_result)

    print("\nFinance Result:")
    print(finance_result)

    messages = [
        {
            "role": "system",
            "content": """
You are a Recommendation Agent.

You receive information from other specialized agents.

Your job is to combine the information and provide
a useful recommendation to the user.

You have received information from:

1. User Agent
2. Weather Agent
3. Finance Agent

Do not mention A2A, MCP, agents, JSON or internal processing.

Give a natural and useful answer to the user.
"""
        },
        {
            "role": "user",
            "content": f"""
USER INFORMATION:
{user_result}

WEATHER INFORMATION:
{weather_result}

FINANCE INFORMATION:
{finance_result}

Based on all this information, provide a useful recommendation.
"""
        }
    ]

    response = chat_llm(messages)

    result = response.choices[0].message.content

    print("\nRecommendation:")
    print(result)

    return result
