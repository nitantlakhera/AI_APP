import yaml
from mcp import Client


class MCPManager:

    def __init__(self):

        # Load MCP servers
        self.mcp_servers = self.get_mcp_servers()

        # Tool registry
        self.tool_registry = {}

        # All tools in OpenAI format
        self.all_tools = []

    # ========================================================
    # GET MCP SERVERS
    # ========================================================

    def get_mcp_servers(self):

        with open("mcp_servers.yaml", "r") as file:
            config = yaml.safe_load(file)

        return {
            name: server["url"]
            for name, server in config["servers"].items()
        }

    # ========================================================
    # CONVERT MCP TOOL -> OPENAI TOOL
    # ========================================================

    def mcp_tool_to_openai_tool(
            self,
            server_name,
            mcp_tool
    ):

        tool_name = mcp_tool.name

        description = mcp_tool.description or (
            f"Tool provided by {server_name} MCP server"
        )

        input_schema = mcp_tool.input_schema

        openai_tool = {

            "type": "function",

            "function": {

                "name": tool_name,

                "description": description,

                "parameters": input_schema
            }
        }

        # Store information about this tool
        self.tool_registry[tool_name] = {

            "server": server_name,

            "url": self.mcp_servers[server_name]
        }

        return openai_tool

    # ========================================================
    # DISCOVER ALL MCP TOOLS
    # ========================================================

    async def discover_tools(self):

        print("\n========================================")
        print("DISCOVERING MCP TOOLS")
        print("========================================")

        self.all_tools = []

        for server_name, server_url in self.mcp_servers.items():

            print(f"\nConnecting to: {server_name}")
            print(f"URL: {server_url}")

            async with Client(server_url) as mcp_client:

                response = await mcp_client.list_tools()

                print(
                    f"\nTools from {server_name} MCP:"
                )

                for mcp_tool in response.tools:
                    print(
                        f"  - {mcp_tool.name}"
                    )

                    openai_tool = (
                        self.mcp_tool_to_openai_tool(
                            server_name,
                            mcp_tool
                        )
                    )

                    self.all_tools.append(
                        openai_tool
                    )

        print("\n========================================")
        print("DISCOVERED TOOLS")
        print("========================================")

        for tool in self.all_tools:
            print(
                " -",
                tool["function"]["name"]
            )

        return self.all_tools

    # ========================================================
    # GET TOOLS FOR ONE AGENT
    # ========================================================

    def get_tools_for_server(self, server_name):

        tools = []

        for tool in self.all_tools:

            tool_name = tool["function"]["name"]

            tool_info = self.tool_registry[tool_name]

            if tool_info["server"] == server_name:
                tools.append(tool)

        return tools

    # ========================================================
    # CALL MCP TOOL
    # ========================================================

    async def call_mcp_tool(
            self,
            tool_name,
            arguments
    ):

        # Check if tool exists
        if tool_name not in self.tool_registry:
            return {
                "error":
                    f"Tool '{tool_name}' not found"
            }

        # Get tool information
        tool_info = self.tool_registry[tool_name]

        server_name = tool_info["server"]

        server_url = tool_info["url"]

        print("\n========================================")
        print("MCP TOOL EXECUTION")
        print("========================================")

        print("Tool:", tool_name)
        print("Server:", server_name)
        print("Arguments:", arguments)

        # Connect to correct MCP server
        async with Client(server_url) as mcp_client:

            result = await mcp_client.call_tool(

                tool_name,

                arguments
            )

            print("\nMCP RESULT:")
            print(result)

            if result.structured_content:
                return result.structured_content

            return {
                "content": str(result.content)
            }
