"""Placeholder PromptManager for the MCP shim.

Implement prompt templates, parameterization and rendering here.
"""
from __future__ import annotations

from typing import Any, Dict


class PromptManager:
    def __init__(self) -> None:
        self._prompts: Dict[str, Any] = {}

    def register(self, prompt_id: str, template: str) -> None:
        self._prompts[prompt_id] = template

    def render(self, prompt_id: str, **kwargs) -> str:
        template = self._prompts[prompt_id]
        return template.format(**kwargs)

    def list(self) -> list[str]:
        return list(self._prompts.keys())
