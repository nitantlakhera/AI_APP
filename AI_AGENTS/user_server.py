from mcp.server import MCPServer

mcp = MCPServer("User Server")


@mcp.tool()
def get_user_info(user_id: int) -> dict:
    users = {
        101: {
            "name": "Rahul",
            "city": "Bangalore",
            "role": "Software Engineer"
        },
        102: {
            "name": "Amit",
            "city": "Delhi",
            "role": "Manager"
        }
    }

    return users.get(
        user_id,
        {"error": f"User {user_id} not found"}
    )


if __name__ == "__main__":
    mcp.run(
        "streamable-http",
        port=8003
    )
