import os
import psycopg2
from dotenv import load_dotenv
from agentic_ai.agents.llm_provider import chat_llm_tools
import json

load_dotenv()


# ============================================================
# USER AGENT
# ============================================================


def get_user_from_db(user_id):
    connection = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

    try:
        cursor = connection.cursor()

        query = """
            SELECT id, name, city, role
            FROM agents.users
            WHERE id = %s
        """

        cursor.execute(query, (user_id,))

        row = cursor.fetchone()

        if row is None:
            return {
                "error": f"User {user_id} not found"
            }

        return {
            "id": row[0],
            "name": row[1],
            "city": row[2],
            "role": row[3]
        }

    finally:
        cursor.close()
        connection.close()


def user_agent(question):
    print("\n========================================")
    print("USER AGENT")
    print("========================================")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. "
                "When the user asks for information about a user, "
                "use the available database tool."
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_user_from_db",
                "description": "Get user information from PostgreSQL using the user ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "integer",
                            "description": "The ID of the user"
                        }
                    },
                    "required": ["user_id"]
                }
            }
        }
    ]

    # {
    #     "tool_calls": [
    #         {
    #             "function": {
    #                 "name": "get_user_from_db",
    #                 "arguments": {
    #                     "user_id": 101
    #                 }
    #             }
    #         }
    #     ]
    # }

    # ========================================================
    # AGENT LOOP
    # ========================================================

    while True:
        print("\n ======== Calling LLM ==========")

        response = chat_llm_tools(messages, tools)

        message = response.choices[0].message

        # Add LLM response to conversation
        messages.append(message)

        # ====================================================
        # NO TOOL CALL
        # ====================================================

        if not message.tool_calls:
            return message.content

        # ====================================================
        # NO TOOL CALL
        # ====================================================

        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(tool_call.function.arguments)

            print("\n====== TOOL CALL ======")
            print("Tool:", tool_name)
            print("Arguments:", arguments)

            # ----------------------------------------------
            # Execute tool
            # ----------------------------------------------

            if tool_name == "get_user_from_db":

                result = get_user_from_db(**arguments)
            else:

                result = {"error": f"Unknown tool: {tool_name}"}

            # ----------------------------------------------
            # Send tool result back to LLM
            # ----------------------------------------------

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                }
            )

        continue


if __name__ == "__main__":
    result = user_agent("What are the details of user 101?")
    print(result)
