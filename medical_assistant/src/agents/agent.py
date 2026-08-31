"""Medical AI agent — uses healthcare tools in a ReAct loop."""

from __future__ import annotations

from dataclasses import dataclass, field

from medical_assistant.src.agents.tools import TOOL_SCHEMAS, execute_tool
from medical_assistant.src.config import settings
from medical_assistant.src.llm_bridge import Message, llm

AGENT_PROMPT = """You are a medical education agent for students learning healthcare AI.

RULES:
- EDUCATIONAL ONLY — never provide real diagnoses or prescriptions
- Always recommend consulting a qualified doctor for health concerns
- Use tools when needed: BMI calculator, symptom lookup, medication info, specialist finder, medical KB search

Available tools: bmi_calculator, symptom_lookup, medication_info, find_specialist, search_medical_kb

Be clear, helpful, and always include educational disclaimers."""


@dataclass
class AgentStep:
    step_number: int
    thought: str
    tool_name: str | None = None
    tool_input: dict | None = None
    tool_output: str | None = None


@dataclass
class AgentResult:
    answer: str
    steps: list[AgentStep] = field(default_factory=list)
    total_steps: int = 0


class MedicalAgent:
    """ReAct agent with medical education tools."""

    def __init__(self, max_steps: int | None = None) -> None:
        self.max_steps = max_steps or settings.max_agent_steps

    def run(self, user_query: str) -> AgentResult:
        messages = [
            Message(role="system", content=AGENT_PROMPT),
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
                steps.append(AgentStep(step_number=step_num, thought="Direct answer"))
                answer = response.content + "\n\n⚠️ Educational only — consult a doctor for health concerns."
                return AgentResult(answer=answer, steps=steps, total_steps=step_num)

        final_response = llm.chat(messages, temperature=0.3)
        answer = final_response.content.strip()
        if not answer:
            answer = steps[-1].tool_output if steps and steps[-1].tool_output else (
                "Reached maximum steps without a final answer."
            )
        answer += "\n\n⚠️ Educational only — consult a doctor for health concerns."
        return AgentResult(answer=answer, steps=steps, total_steps=self.max_steps)
