import sys
from pathlib import Path

import streamlit as st

# Add AI_APP to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_ai.multi_agents.multi_agent import run_multi_agent

st.set_page_config(
    page_title="AI Multi-Agent Assistant",
    page_icon="🤖"
)

st.title("🤖 AI Multi-Agent Assistant")

st.write(
    "Ask me something and I'll route your request "
    "to the appropriate agent."
)

question = st.chat_input("Ask me anything...")

if question:
    # Display user's question
    with st.chat_message("user"):
        st.write(question)

    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = run_multi_agent(question)

        st.write(answer)

# if __name__ == "__main__":
#     print("User typed the questions")
#
#     run_multi_agent("What is the weather in Bangalore?")
