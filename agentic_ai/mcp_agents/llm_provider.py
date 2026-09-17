import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
# ============================================================
# OLLAMA
# ============================================================

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
API_KEY = os.getenv("LLM_PROVIDER")
MODEL_NAME = os.getenv("OLLAMA_MODEL")


def get_llm():
    llm = OpenAI(
        base_url=f"{OLLAMA_BASE_URL}/v1",
        api_key=API_KEY
    )
    return llm


# This function is for agents whose need to invoke tools
def chat_llm_tools(messages, tools):
    response = get_llm().chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    return response


# This function is for supervisor Agent, because he doesn't need any tools to use
def chat_llm(messages):
    response = get_llm().chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tool_choice="auto"
    )
    return response
