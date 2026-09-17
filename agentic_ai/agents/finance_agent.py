from agentic_ai.agents.llm_provider import chat_llm_tools
import json


# ============================================================
# FINANCE AGENT
# ============================================================


def finance_agent(question):
    print("\n========================================")
    print("FINANCE AGENT")
    print("========================================")

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_exchange_rate",
                "description": (
                    "Get exchange rate between two currencies."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "from_currency": {
                            "type": "string"
                        },
                        "to_currency": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "from_currency",
                        "to_currency"
                    ]
                }
            }
        }
    ]

    messages = [
        {
            "role": "system",
            "content": (
                "You are a Finance Agent. "
                "Use get_exchange_rate for currency questions."
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]

    while True:

        # Get LLM response
        response = chat_llm_tools(messages, tools)

        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:

            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:

                tool_name = tool_call.function.name

                arguments = json.loads(
                    tool_call.function.arguments
                )

                if tool_name == "get_exchange_rate":

                    rates = {
                        "USD_INR": 88.0,
                        "EUR_INR": 103.0,
                        "GBP_INR": 119.0,
                        "INR_USD": 0.0114,
                        "INR_EUR": 0.0097,
                        "INR_GBP": 0.0084
                    }

                    key = (
                        f"{arguments['from_currency'].upper()}_"
                        f"{arguments['to_currency'].upper()}"
                    )

                    result = {
                        "rate": rates.get(
                            key,
                            "Rate not available"
                        )
                    }

                else:

                    result = {
                        "error": f"Unknown tool: {tool_name}"
                    }

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

            continue

        return assistant_message.content


if __name__ == "__main__":
    result = finance_agent("What is USD to INR?");
    print(result)
