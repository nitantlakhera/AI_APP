import os
import psycopg2
from dotenv import load_dotenv
from mcp.server import FastMCP

# mcp = MCPServer("User Server")

mcp = FastMCP(
    "User Server",
    host="127.0.0.1",
    port=8002
)

load_dotenv()


# ============================================================
# DATABASE TOOL
# ============================================================

@mcp.tool()
def get_user_from_db(user_id):
    return get_db_records(user_id)


def get_db_records(user_id):
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


if __name__ == "__main__":
    mcp.run(
        "streamable-http"
    )
