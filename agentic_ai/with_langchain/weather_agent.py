import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI


load_dotenv()


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
API_KEY = os.getenv("LLM_PROVIDER")
MODEL_NAME = os.getenv("OLLAMA_MODEL")


# ============================================================
# MAIN
# ============================================================

async def main():

    # ========================================================
    # MCP CLIENT
    # ========================================================

    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "streamable_http",
                "url": "http://localhost:8003/mcp"
            }
        }
    )

    # ========================================================
    # GET MCP TOOLS
    # ========================================================

    tools = await client.get_tools()

    print("Available tools:")

    for tool in tools:
        print("-", tool.name)

    # ========================================================
    # LLM - OLLAMA
    # ========================================================

    llm = ChatOpenAI(
        model=MODEL_NAME,
        base_url=f"{OLLAMA_BASE_URL}/v1",
        api_key=API_KEY,
        temperature=0
    )

    # ========================================================
    # CREATE AGENT
    # ========================================================

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are a weather assistant. "
            "Use the weather tool when necessary. "
            "After receiving weather data, "
            "answer the user in natural plain English."
        )
    )

    # ========================================================
    # RUN AGENT
    # ========================================================

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "What is the weather in Bangalore?"
                }
            ]
        }
    )

    # ========================================================
    # FINAL ANSWER
    # ========================================================

    print("\n========================================")
    print("FINAL ANSWER")
    print("========================================")

    print(result["messages"][-1].content)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())