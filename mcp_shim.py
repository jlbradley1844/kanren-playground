#!/usr/bin/env python3
"""
mcp_shim.py

Small executable shim to start an MCP-style server. This is a minimal template you can extend by
implementing resources, tools and prompts in the `mcp` package.

Usage:
    python mcp_shim.py --host 127.0.0.1 --port 31337

Run as executable (optional):
    chmod +x mcp_shim.py
    ./mcp_shim.py
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import signal
from mcp.server import MCPServer
from mcp.resources import ResourceManager
from mcp.tools import ToolManager
from mcp.prompts import PromptManager

logger = logging.getLogger("mcp_shim")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="MCP server shim")
    p.add_argument("--host", default="127.0.0.1", help="Host to bind")
    p.add_argument("--port", type=int, default=31337, help="Port to bind")
    p.add_argument("--debug", action="store_true", help="Enable debug logging")
    return p.parse_args()


async def run_server(host: str, port: int, debug: bool) -> None:
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    resources = ResourceManager()
    tools = ToolManager()
    prompts = PromptManager()

    server = MCPServer(host=host, port=port, resources=resources, tools=tools, prompts=prompts)

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _on_signal(*_):
        logger.info("received stop signal")
        stop_event.set()

    loop.add_signal_handler(signal.SIGINT, _on_signal)
    loop.add_signal_handler(signal.SIGTERM, _on_signal)

    await server.start()
    logger.info("server started on %s:%d", host, port)

    try:
        await stop_event.wait()
    finally:
        logger.info("shutting down server")
        await server.stop()


def main():
    args = parse_args()
    try:
        asyncio.run(run_server(args.host, args.port, args.debug))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
