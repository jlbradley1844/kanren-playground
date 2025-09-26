"""Placeholder ResourceManager for the MCP shim.

Implement resource loading/access in this module.
"""
from __future__ import annotations

from typing import Any, Dict


class ResourceManager:
    def __init__(self) -> None:
        self._resources: Dict[str, Any] = {}

    def register(self, name: str, obj: Any) -> None:
        """Register a resource by name."""
        self._resources[name] = obj

    def get(self, name: str) -> Any:
        """Return the resource or raise KeyError."""
        return self._resources[name]

    def list(self) -> list[str]:
        return list(self._resources.keys())
