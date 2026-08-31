"""Medical chat service with healthcare tutor persona."""

from __future__ import annotations

from dataclasses import dataclass, field

from medical_assistant.src.llm_bridge import Message, llm

MEDICAL_SYSTEM_PROMPT = """You are a medical education tutor for the Medical Assistant Learning Lab.

IMPORTANT RULES:
- This is an EDUCATIONAL project only — NOT real medical advice
- Always remind users to consult a qualified doctor for health concerns
- Explain medical concepts in simple, beginner-friendly language
- Use general health education knowledge from the learning materials
- Never diagnose conditions or prescribe treatments
- If asked about emergencies, tell the user to call emergency services immediately

Your role: help students learn about human biology, common conditions, first aid basics,
nutrition, and medical terminology."""


@dataclass
class MedicalChatSession:
    """Multi-turn medical education chat with conversation memory."""

    system_prompt: str = MEDICAL_SYSTEM_PROMPT
    messages: list[Message] = field(default_factory=list)
    max_history: int = 20

    def __post_init__(self) -> None:
        if not any(m.role == "system" for m in self.messages):
            self.messages.insert(0, Message(role="system", content=self.system_prompt))

    def send(self, user_message: str) -> str:
        previous_messages = self.messages.copy()
        self.messages.append(Message(role="user", content=user_message))
        self._trim_history()
        try:
            response = llm.chat(self.messages, temperature=0.5)
        except Exception:
            self.messages = previous_messages
            raise
        reply = response.content
        self.messages.append(Message(role="assistant", content=reply))
        return reply

    def clear(self) -> None:
        self.messages = [Message(role="system", content=self.system_prompt)]

    def get_history_display(self) -> list[dict[str, str]]:
        return [
            {"role": m.role, "content": m.content}
            for m in self.messages
            if m.role in ("user", "assistant")
        ]

    def _trim_history(self) -> None:
        system_msgs = [m for m in self.messages if m.role == "system"]
        other_msgs = [m for m in self.messages if m.role != "system"]
        if len(other_msgs) > self.max_history:
            other_msgs = other_msgs[-self.max_history :]
        self.messages = system_msgs + other_msgs
