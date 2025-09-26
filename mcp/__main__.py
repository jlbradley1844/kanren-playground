"""Console entrypoint for mcp package.

Usage: python -m mcp or via installed console script `mcp-shim`.
"""
from __future__ import annotations

from argparse import ArgumentParser
from mcp.server import MCPServer
from mcp.resources import ResourceManager
from mcp.tools import ToolManager
from mcp.prompts import PromptManager
import asyncio
import logging
import signal


def main(argv=None):
    parser = ArgumentParser(prog="mcp-shim")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=31337)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args(argv)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    resources = ResourceManager()
    tools = ToolManager()
    prompts = PromptManager()

    server = MCPServer(host=args.host, port=args.port, resources=resources, tools=tools, prompts=prompts)

    async def run():
        loop = asyncio.get_running_loop()
        stop_event = asyncio.Event()

        def _on_signal(*_):
            stop_event.set()

        try:
            loop.add_signal_handler(signal.SIGINT, _on_signal)
            loop.add_signal_handler(signal.SIGTERM, _on_signal)
        except NotImplementedError:
            # Some platforms (Windows/limited containers) don't support add_signal_handler
            pass

        await server.start()
        try:
            await stop_event.wait()
        finally:
            await server.stop()

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
