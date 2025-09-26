"""Simple asyncio-based MCP server skeleton.

This implements a tiny line-delimited JSON protocol as a starting point. Clients send JSON
messages (newline-terminated). The server dispatches to a simple `on_request` hook that can be
implemented using resources/tools/prompts managers.

This is intentionally minimal; extend it to match the real MCP spec you plan to implement.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Optional

logger = logging.getLogger("mcp.server")


class MCPServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 31337, *, resources=None, tools=None, prompts=None):
        self.host = host
        self.port = port
        self._server: Optional[asyncio.AbstractServer] = None
        self._resources = resources
        self._tools = tools
        self._prompts = prompts
        self._clients: set[asyncio.Task] = set()

    async def start(self) -> None:
        self._server = await asyncio.start_server(self._handle_client, self.host, self.port)
        logger.info("MCPServer listening on %s:%d", self.host, self.port)

    async def stop(self) -> None:
        if self._server is None:
            return
        # Stop accepting new connections
        self._server.close()
        await self._server.wait_closed()
        # Cancel client tasks
        for task in list(self._clients):
            task.cancel()
        await asyncio.gather(*self._clients, return_exceptions=True)
        self._clients.clear()
        logger.info("MCPServer stopped")

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info("peername")
        logger.info("client connected: %s", addr)
        task = asyncio.current_task()
        if task is not None:
            self._clients.add(task)

        try:
            # Send a welcome / ready message
            await self._send_json(writer, {"type": "ready"})

            while True:
                line = await reader.readline()
                if not line:
                    break
                try:
                    message = json.loads(line.decode("utf8"))
                except Exception:
                    logger.exception("failed to decode incoming message")
                    await self._send_json(writer, {"type": "error", "reason": "invalid_json"})
                    continue

                # Dispatch
                try:
                    response = await self.on_request(message)
                except Exception as exc:  # pragma: no cover - behaviour depends on user code
                    logger.exception("error in request handler")
                    response = {"type": "error", "reason": str(exc)}

                if response is not None:
                    await self._send_json(writer, response)

        except asyncio.CancelledError:
            logger.debug("client handler cancelled")
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
            logger.info("client disconnected: %s", addr)
            if task is not None:
                self._clients.discard(task)

    async def _send_json(self, writer: asyncio.StreamWriter, obj: object) -> None:
        payload = (json.dumps(obj, separators=(",", ":")) + "\n").encode("utf8")
        writer.write(payload)
        await writer.drain()

    async def on_request(self, message: dict) -> Optional[dict]:
        """Handle an incoming request message and return a response dict or None.

        Default behaviour: simple echo for messages of type 'echo', and a small dispatch for
        'resource', 'tool', 'prompt' messages that shows where you can integrate your components.
        Override or monkeypatch this method in your app to provide real behaviour.
        """
        mtype = message.get("type")
        logger.debug("on_request: %s", mtype)

        if mtype == "echo":
            return {"type": "echo", "payload": message.get("payload")}

        if mtype == "resource":
            name = message.get("name")
            if self._resources is None:
                return {"type": "error", "reason": "no_resources"}
            # example hook: resources.get(name).call(...)
            return {"type": "resource_response", "name": name}

        if mtype == "tool":
            name = message.get("name")
            if self._tools is None:
                return {"type": "error", "reason": "no_tools"}
            return {"type": "tool_response", "name": name}

        if mtype == "prompt":
            pid = message.get("prompt_id")
            if self._prompts is None:
                return {"type": "error", "reason": "no_prompts"}
            return {"type": "prompt_response", "prompt_id": pid}

        return {"type": "error", "reason": "unknown_type"}
