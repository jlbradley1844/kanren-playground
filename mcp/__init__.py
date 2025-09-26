"""mcp package: lightweight placeholders for server components."""
from .server import MCPServer
from .resources import ResourceManager
from .tools import ToolManager
from .prompts import PromptManager

__all__ = ["MCPServer", "ResourceManager", "ToolManager", "PromptManager"]
