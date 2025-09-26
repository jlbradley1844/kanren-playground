#!/usr/bin/env python3
"""
Demo: run_demo
===============

This script starts a tiny MCP-style server (a `DemoServer` subclass) and then
issues a few example JSON requests to it. The demo shows an end-to-end flow:

- Start the server (runs in-process)
- Send an `echo` request
- Send `rule` requests that exercise the `krules` helpers (descendants,
    ancestors, role assignment, role checks)

How to run
----------
Run the demo from the repository root so local packages are importable:

```sh
. venv/bin/activate
PYTHONPATH=. python examples/run_demo.py
```

What the demo does (example requests)
-------------------------------------
- Echo: {"type": "echo", "payload": "hello demo"}
- Descendants: {"type": "rule", "action": "descendants", "who": "bob"}
- Ancestors: {"type": "rule", "action": "ancestors", "who": "sue"}
- Assign role: {"type": "rule", "action": "assign_role", "role": "admin", "who": "alice"}
- Has role: {"type": "rule", "action": "has_role", "role": "admin", "who": "alice"}

Sample output (what you should see printed)
-------------------------------------------
echo response: {'type': 'echo', 'payload': 'hello demo'}
descendants of bob: {'type': 'rule_response', 'descendants': ['alice', 'jack', 'sue']}
ancestors of sue: {'type': 'rule_response', 'ancestors': ['bob', 'alice']}
assign role response: {'type': 'rule_response', 'assigned': True}
has_role alice admin: {'type': 'rule_response', 'has_role': True}

Notes
-----
- This is a small, synchronous demo for local development and testing. The
    server implementation is intentionally minimal — extend `DemoServer` or
    `MCPServer` to integrate production resources and tools.

No logical code changes are made to this file beyond replacing the module
docstring with the demo documentation above.
"""
from __future__ import annotations

import asyncio
import json
import logging
from mcp.server import MCPServer
from mcp.resources import ResourceManager
from mcp.tools import ToolManager
from mcp.prompts import PromptManager

from krules.helpers import descendants_of, ancestors_of, assign_role, has_role

logger = logging.getLogger("run_demo")


class DemoServer(MCPServer):
    async def on_request(self, message: dict):
        # handle rule messages using krules helpers
        if message.get("type") == "rule":
            action = message.get("action")
            if action == "descendants":
                who = message.get("who")
                if not isinstance(who, str):
                    return {"type": "error", "reason": "missing_or_invalid_who"}
                return {"type": "rule_response", "descendants": descendants_of(who)}

            if action == "ancestors":
                who = message.get("who")
                if not isinstance(who, str):
                    return {"type": "error", "reason": "missing_or_invalid_who"}
                return {"type": "rule_response", "ancestors": ancestors_of(who)}

            if action == "assign_role":
                role = message.get("role")
                who = message.get("who")
                if not isinstance(role, str) or not isinstance(who, str):
                    return {"type": "error", "reason": "missing_or_invalid_role_or_who"}
                assign_role(role, who)
                return {"type": "rule_response", "assigned": True}

            if action == "has_role":
                role = message.get("role")
                who = message.get("who")
                if not isinstance(role, str) or not isinstance(who, str):
                    return {"type": "error", "reason": "missing_or_invalid_role_or_who"}
                return {"type": "rule_response", "has_role": has_role(role, who)}

        # fallback to base server behaviour
        return await super().on_request(message)


async def send_message(host: str, port: int, payload: dict) -> dict:
    reader, writer = await asyncio.open_connection(host, port)
    # Read server welcome/ready message which MCPServer sends on connect
    _ready = await reader.readline()

    data = (json.dumps(payload) + "\n").encode("utf8")
    writer.write(data)
    await writer.drain()

    # Now read the response for our request
    line = await reader.readline()

    try:
        writer.close()
        await writer.wait_closed()
    except Exception:
        # ignore connection reset during demo shutdown
        pass

    if not line:
        return {}
    return json.loads(line.decode("utf8"))


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    host = "127.0.0.1"
    port = 31339

    resources = ResourceManager()
    tools = ToolManager()
    prompts = PromptManager()

    server = DemoServer(host=host, port=port, resources=resources, tools=tools, prompts=prompts)

    await server.start()
    logger.info("demo server started on %s:%d", host, port)

    try:
        # echo
        r = await send_message(host, port, {"type": "echo", "payload": "hello demo"})
        print("echo response:", r)

        # query descendants
        r = await send_message(host, port, {"type": "rule", "action": "descendants", "who": "bob"})
        print("descendants of bob:", r)

        # query ancestors
        r = await send_message(host, port, {"type": "rule", "action": "ancestors", "who": "sue"})
        print("ancestors of sue:", r)

        # assign a role and query
        r = await send_message(host, port, {"type": "rule", "action": "assign_role", "role": "admin", "who": "alice"})
        print("assign role response:", r)

        r = await send_message(host, port, {"type": "rule", "action": "has_role", "role": "admin", "who": "alice"})
        print("has_role alice admin:", r)

    finally:
        await server.stop()
        logger.info("demo server stopped")


if __name__ == "__main__":
    asyncio.run(main())
