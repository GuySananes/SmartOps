from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import anthropic

from core import config


class BaseAgent(ABC):
    name: str
    prompt_file: str

    def __init__(self) -> None:
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.system_prompt = self._load_prompt(self.prompt_file)

    def _load_prompt(self, filename: str) -> str:
        path = Path(__file__).parent.parent / ".claude" / "prompts" / filename
        if path.exists():
            return path.read_text(encoding="utf-8")
        return f"You are the {self.name} agent for SmartOps, a multi-agent task management system."

    @abstractmethod
    def _get_tools(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def _execute_tool(self, name: str, tool_input: dict[str, Any]) -> str:
        pass

    def run(self, user_message: str) -> str:
        messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]

        while True:
            response = self.client.messages.create(
                model=config.MODEL_ID,
                max_tokens=4096,
                system=self.system_prompt,
                tools=self._get_tools(),  # type: ignore[arg-type]
                messages=messages,  # type: ignore[arg-type]
            )

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text"):
                        return block.text  # type: ignore[attr-defined]
                return ""

            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = self._execute_tool(block.name, block.input)  # type: ignore[attr-defined]
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,  # type: ignore[attr-defined]
                                "content": result,
                            }
                        )
                messages.append({"role": "user", "content": tool_results})
            else:
                break

        return "Agent completed without a final response."
