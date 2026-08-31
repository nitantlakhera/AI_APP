"""AI Agent — LLM that can reason and use tools in a loop."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.agents.tools import TOOL_SCHEMAS, execute_tool
from src.config import settings
from src.llm.provider import Message, llm


@dataclass
class AgentStep:
    """One step in the agent's reasoning loop."""

    step_number: int
    thought: str
    tool_name: str | None = None
    tool_input: dict | None = None
    tool_output: str | None = None


@dataclass
class AgentResult:
    """Final result from an agent run."""

    answer: str
    steps: list[AgentStep] = field(default_factory=list)
    total_steps: int = 0


AGENT_SYSTEM_PROMPT = """You are an AI agent that can use tools to help answer questions.
Available tools: calculator, get_weather, get_current_time, search_knowledge, search_wiki.

Use search_knowledge for semantic retrieval from raw document chunks (RAG).
Use search_wiki for keyword retrieval from compiled markdown wiki pages.

Think step by step:
1. Understand what the user needs
2. Decide if you need a tool or can answer directly
3. Use tools when needed, then synthesize the final answer

Be concise and helpful."""


class Agent:
    """
    ReAct-style agent: Reason + Act loop.

    Concept: Agentic AI
    - The LLM decides WHICH tool to use and WHEN
    - It runs tools, observes results, and may call more tools
    - This loop continues until the agent has a final answer

    Flow:
    User Query → LLM thinks → (optional) Tool Call → Tool Result → LLM thinks → ... → Final Answer
    """

    def __init__(self, max_steps: int | None = None) -> None:
        self.max_steps = settings.max_agent_steps if max_steps is None else max_steps
        if self.max_steps <= 0:
            raise ValueError("max_steps must be greater than zero")

    def run(self, user_query: str) -> AgentResult:
        messages = [
            Message(role="system", content=AGENT_SYSTEM_PROMPT),
            Message(role="user", content=user_query),
        ]
        steps: list[AgentStep] = []

        for step_num in range(1, self.max_steps + 1):
            response = llm.chat(messages, tools=TOOL_SCHEMAS, temperature=0.3)

            if response.tool_calls:
                messages.append(Message(
                    role="assistant",
                    content=response.content,
                    tool_calls=response.tool_calls,
                ))
                for tc in response.tool_calls:
                    tool_output = execute_tool(tc.name, tc.arguments)

                    steps.append(AgentStep(
                        step_number=step_num,
                        thought=f"Calling tool: {tc.name}",
                        tool_name=tc.name,
                        tool_input=tc.arguments,
                        tool_output=tool_output,
                    ))

                    messages.append(Message(
                        role="tool",
                        content=tool_output,
                        name=tc.name,
                        tool_call_id=tc.id,
                    ))
            else:
                steps.append(AgentStep(
                    step_number=step_num,
                    thought="Direct answer (no tool needed)",
                ))
                return AgentResult(
                    answer=response.content,
                    steps=steps,
                    total_steps=step_num,
                )

        final_response = llm.chat(messages, temperature=0.3)
        answer = final_response.content.strip()
        if not answer:
            answer = steps[-1].tool_output if steps and steps[-1].tool_output else (
                "Reached maximum steps without a final answer."
            )
        return AgentResult(answer=answer, steps=steps, total_steps=self.max_steps)
