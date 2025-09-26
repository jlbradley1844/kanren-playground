"""Placeholder ToolManager for the MCP shim.
"""
from __future__ import annotations

from typing import Any, Dict


class ToolManager:
    def __init__(self) -> None:
        self._tools: Dict[str, Any] = {}

    def register(self, name: str, callable_obj) -> None:
        self._tools[name] = callable_obj

    def call(self, name: str, *args, **kwargs):
        if name not in self._tools:
            raise KeyError(name)
        return self._tools[name](*args, **kwargs)

    def list(self) -> list[str]:
        return list(self._tools.keys())
