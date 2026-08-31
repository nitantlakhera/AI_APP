"""Chat service with conversation memory."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.llm.provider import Message, llm


@dataclass
class ChatSession:
    """
    Manages a multi-turn conversation.

    Concept: Generative AI Chat
    - The model sees the full conversation history (context window)
    - System prompt sets the assistant's personality and rules
    - Each turn: user message → model generates assistant reply
    """

    system_prompt: str = (
        "You are a helpful AI tutor for the AI Learning Lab. "
        "Explain concepts clearly and simply for beginners."
    )
    messages: list[Message] = field(default_factory=list)
    max_history: int = 20

    def __post_init__(self) -> None:
        if not any(m.role == "system" for m in self.messages):
            self.messages.insert(0, Message(role="system", content=self.system_prompt))

    def send(self, user_message: str) -> str:
        """Send a user message and return the assistant reply."""
        previous_messages = self.messages.copy()
        self.messages.append(Message(role="user", content=user_message))
        self._trim_history()

        try:
            response = llm.chat(self.messages)
        except Exception:
            self.messages = previous_messages
            raise
        reply = response.content

        self.messages.append(Message(role="assistant", content=reply))
        return reply

    def clear(self) -> None:
        """Reset conversation, keeping only the system prompt."""
        self.messages = [Message(role="system", content=self.system_prompt)]

    def _trim_history(self) -> None:
        """Keep conversation within max_history (excluding system message)."""
        system_msgs = [m for m in self.messages if m.role == "system"]
        other_msgs = [m for m in self.messages if m.role != "system"]
        if len(other_msgs) > self.max_history:
            other_msgs = other_msgs[-self.max_history :]
        self.messages = system_msgs + other_msgs

    def get_history_display(self) -> list[dict[str, str]]:
        """Return messages for UI display (excludes system prompt)."""
        return [
            {"role": m.role, "content": m.content}
            for m in self.messages
            if m.role in ("user", "assistant")
        ]
