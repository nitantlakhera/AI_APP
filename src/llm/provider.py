"""LLM provider abstraction — supports Ollama, OpenAI, and demo mode."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

import httpx
from openai import OpenAI

from src.config import settings


@dataclass
class ToolCall:
    """A tool call requested by the LLM."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class Message:
    """A single chat message."""

    role: str  # "system" | "user" | "assistant" | "tool"
    content: str
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)


@dataclass
class LLMResponse:
    """Response from the LLM."""

    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str = "stop"


class LLMProvider:
    """
    Unified interface for different LLM backends.

    Concepts covered:
    - Generative AI: text generation from a language model
    - Prompting: system + user messages shape model behavior
    - Tool calling: models can request external tools (agentic AI)
    """

    def __init__(self) -> None:
        self.provider = settings.llm_provider.lower()
        self._client: OpenAI | None = None

    @property
    def is_demo_mode(self) -> bool:
        return self.provider == "demo"

    def _get_openai_client(self) -> OpenAI:
        if self._client is None:
            if self.provider == "ollama":
                self._client = OpenAI(
                    base_url=f"{settings.ollama_base_url}/v1",
                    api_key="ollama",
                )
            else:
                self._client = OpenAI(api_key=settings.openai_api_key)
        return self._client

    def _model_name(self) -> str:
        if self.provider == "ollama":
            return settings.ollama_model
        if self.provider == "openai":
            return settings.openai_model
        return "demo"

    def check_connection(self) -> dict[str, Any]:
        """Check if the configured LLM is reachable."""
        if self.is_demo_mode:
            return {"status": "ok", "provider": "demo", "message": "Demo mode — no LLM needed"}

        if self.provider == "ollama":
            try:
                resp = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=5)
                resp.raise_for_status()
                models = [m["name"] for m in resp.json().get("models", [])]
                return {
                    "status": "ok",
                    "provider": "ollama",
                    "models": models,
                    "configured_model": settings.ollama_model,
                    "verified": True,
                }
            except Exception as exc:
                return {"status": "error", "provider": "ollama", "message": str(exc)}

        if self.provider == "openai":
            if not settings.openai_api_key or settings.openai_api_key.startswith("sk-your"):
                return {"status": "error", "provider": "openai", "message": "OPENAI_API_KEY not set"}
            return {
                "status": "ok",
                "provider": "openai",
                "configured_model": settings.openai_model,
                "verified": False,
                "message": "API key is configured; connectivity is tested on the first request.",
            }

        return {"status": "error", "message": f"Unknown provider: {self.provider}"}

    def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Send messages to the LLM and get a response."""
        if self.is_demo_mode:
            return self._demo_response(messages, tools)

        client = self._get_openai_client()
        api_messages: list[dict[str, Any]] = []
        for message in messages:
            api_message: dict[str, Any] = {
                "role": message.role,
                "content": message.content,
            }
            if message.name:
                api_message["name"] = message.name
            if message.tool_call_id:
                api_message["tool_call_id"] = message.tool_call_id
            if message.tool_calls:
                api_message["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.name,
                            "arguments": json.dumps(tool_call.arguments),
                        },
                    }
                    for tool_call in message.tool_calls
                ]
            api_messages.append(api_message)

        kwargs: dict[str, Any] = {
            "model": self._model_name(),
            "messages": api_messages,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        content = choice.message.content or ""

        tool_calls: list[ToolCall] = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                raw_arguments = tc.function.arguments
                try:
                    arguments = json.loads(raw_arguments)
                    if not isinstance(arguments, dict):
                        raise ValueError("Tool arguments must be a JSON object")
                except (json.JSONDecodeError, TypeError, ValueError):
                    arguments = {"_invalid_json": raw_arguments}
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=arguments,
                    )
                )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason or "stop",
        )

    def _demo_response(self, messages: list[Message], tools: list[dict] | None) -> LLMResponse:
        """Rule-based responses when no LLM is available — great for learning the flow."""
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        tool_results = [m for m in messages if m.role == "tool"]
        available_tools = {
            tool.get("function", {}).get("name")
            for tool in (tools or [])
        }
        lowered = last_user.lower()

        if tool_results:
            used_tools = {result.name for result in tool_results}
            if (
                "get_current_time" in available_tools
                and "get_current_time" not in used_tools
                and any(phrase in lowered for phrase in ("current time", "what time", "date and time"))
            ):
                return LLMResponse(
                    content="",
                    tool_calls=[
                        ToolCall(id="demo-followup-time", name="get_current_time", arguments={})
                    ],
                    finish_reason="tool_calls",
                )

            if (
                "get_weather" in available_tools
                and "get_weather" not in used_tools
                and "weather" in lowered
            ):
                city_match = re.search(
                    r"weather(?:\s+in)?\s+([a-z ]+?)(?:\s+and\b|\?|$)",
                    lowered,
                )
                city = city_match.group(1).strip().title() if city_match else "London"
                return LLMResponse(
                    content="",
                    tool_calls=[
                        ToolCall(
                            id="demo-followup-weather",
                            name="get_weather",
                            arguments={"city": city},
                        )
                    ],
                    finish_reason="tool_calls",
                )

            formatted_results = "\n\n".join(
                f"- **{result.name or 'tool'}:** {result.content}"
                for result in tool_results
            )
            return LLMResponse(content=f"[Demo Mode] Tool results:\n\n{formatted_results}")

        if any(phrase in lowered for phrase in ("what is my name", "what's my name")):
            for message in reversed(messages):
                if message.role != "user" or message.content == last_user:
                    continue
                name_match = re.search(
                    r"\bmy name is\s+([A-Za-z][A-Za-z'-]*)",
                    message.content,
                    flags=re.IGNORECASE,
                )
                if name_match:
                    return LLMResponse(
                        content=f"[Demo Mode] Your name is {name_match.group(1)}."
                    )

        if "bmi_calculator" in available_tools and "bmi" in lowered:
            numbers = [float(value) for value in re.findall(r"\d+(?:\.\d+)?", last_user)]
            if len(numbers) >= 2:
                return LLMResponse(
                    content="",
                    tool_calls=[
                        ToolCall(
                            id="demo-med-1",
                            name="bmi_calculator",
                            arguments={"weight_kg": numbers[0], "height_m": numbers[1]},
                        )
                    ],
                    finish_reason="tool_calls",
                )

        if "symptom_lookup" in available_tools:
            symptom = next(
                (name for name in ("fever", "headache", "cough", "fatigue") if name in lowered),
                None,
            )
            if symptom:
                return LLMResponse(
                    content="",
                    tool_calls=[
                        ToolCall(
                            id="demo-med-2",
                            name="symptom_lookup",
                            arguments={"symptoms": symptom},
                        )
                    ],
                    finish_reason="tool_calls",
                )

        if "medication_info" in available_tools:
            medication = next(
                (
                    name
                    for name in ("paracetamol", "acetaminophen", "ibuprofen", "amoxicillin", "aspirin")
                    if name in lowered
                ),
                None,
            )
            if medication:
                return LLMResponse(
                    content="",
                    tool_calls=[
                        ToolCall(
                            id="demo-med-3",
                            name="medication_info",
                            arguments={"drug_name": medication},
                        )
                    ],
                    finish_reason="tool_calls",
                )

        if "find_specialist" in available_tools and any(
            term in lowered for term in ("cardiologist", "cardiology", "dermatologist", "dermatology", "pediatric")
        ):
            specialty = next(
                (
                    name
                    for name in ("cardiology", "dermatology", "pediatrics")
                    if name[:6] in lowered
                ),
                "general",
            )
            city_match = re.search(r"\bin\s+([a-z ]+?)(?:\?|$)", lowered)
            city = city_match.group(1).strip().title() if city_match else "your area"
            return LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        id="demo-med-4",
                        name="find_specialist",
                        arguments={"specialty": specialty, "city": city},
                    )
                ],
                finish_reason="tool_calls",
            )

        if "search_medical_kb" in available_tools and any(
            phrase in lowered for phrase in ("medical kb", "medical knowledge", "health documents")
        ):
            return LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        id="demo-med-5",
                        name="search_medical_kb",
                        arguments={"query": last_user},
                    )
                ],
                finish_reason="tool_calls",
            )

        if "calculator" in available_tools and any(
            kw in lowered for kw in ["calculate", "math", "+", "-", "*", "/"]
        ):
            expression = re.sub(
                r"(?is)^.*?(?:calculate|what\s+is)\s+",
                "",
                last_user,
            ).strip().rstrip("?.")
            expression = re.split(
                r"(?i)\s+and\s+(?=(?:the\s+)?(?:weather|time)\b)",
                expression,
                maxsplit=1,
            )[0].strip()
            math_candidate = re.search(
                r"(?:sqrt\s*\([^)]*\)|\d+(?:\.\d+)?)"
                r"(?:\s*[-+*/%]\s*(?:sqrt\s*\([^)]*\)|\d+(?:\.\d+)?))+",
                expression,
                flags=re.IGNORECASE,
            )
            if math_candidate:
                expression = math_candidate.group(0)
            return LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        id="demo-1",
                        name="calculator",
                        arguments={"expression": expression or "2 + 2"},
                    )
                ],
                finish_reason="tool_calls",
            )

        if "get_weather" in available_tools and "weather" in lowered:
            city_match = re.search(
                r"weather(?:\s+in)?\s+([a-z ]+?)(?:\s+and\b|\?|$)",
                lowered,
            )
            city = city_match.group(1).strip().title() if city_match else "London"
            return LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(id="demo-2", name="get_weather", arguments={"city": city})
                ],
                finish_reason="tool_calls",
            )

        if "get_current_time" in available_tools and any(
            phrase in lowered for phrase in ("current time", "what time", "date and time")
        ):
            return LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(id="demo-3", name="get_current_time", arguments={})
                ],
                finish_reason="tool_calls",
            )

        if "search_wiki" in available_tools and any(
            phrase in lowered
            for phrase in ("search the wiki", "search wiki", "wiki knowledge", "open wiki")
        ):
            return LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        id="demo-4",
                        name="search_wiki",
                        arguments={"query": last_user},
                    )
                ],
                finish_reason="tool_calls",
            )

        if "search_knowledge" in available_tools and any(
            phrase in lowered for phrase in ("search the docs", "search documents", "knowledge base")
        ):
            return LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        id="demo-5",
                        name="search_knowledge",
                        arguments={"query": last_user},
                    )
                ],
                finish_reason="tool_calls",
            )

        if "rag" in last_user.lower() or "document" in last_user.lower():
            return LLMResponse(
                content=(
                    "[Demo Mode] RAG retrieves relevant document chunks and augments "
                    "the prompt before generation. Try the RAG tab with sample docs!"
                )
            )

        return LLMResponse(
            content=(
                f"[Demo Mode] You said: '{last_user}'\n\n"
                "I'm running without a real LLM. To use a real model:\n"
                "1. Install Ollama (https://ollama.com) and run: ollama pull llama3.2\n"
                "2. Set LLM_PROVIDER=ollama in .env\n"
                "Or set LLM_PROVIDER=openai with your API key."
            )
        )


# Singleton for the app
llm = LLMProvider()
