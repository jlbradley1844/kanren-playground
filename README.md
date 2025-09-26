mcp-shim — Minimal MCP server shim
===================================

[![CI](https://github.com/jlbradley1844/kanren-playground/actions/workflows/ci.yml/badge.svg)](https://github.com/jlbradley1844/kanren-playground/actions/workflows/ci.yml)

This repository contains a minimal, opinionated template for building an "MCP"-style server in Python.
It's intentionally small so you can extend it with your real resource, tool and prompt implementations.

What's included
---------------
- `mcp/` - package containing the server and manager placeholders:
	- `mcp/server.py` — asyncio-based, line-delimited JSON server and a default `on_request` hook
	- `mcp/resources.py` — `ResourceManager` placeholder
	- `mcp/tools.py` — `ToolManager` placeholder
	- `mcp/prompts.py` — `PromptManager` placeholder
	- `mcp/__main__.py` — package entrypoint (so you can run `python -m mcp` or install the console script)
- `pyproject.toml` — minimal metadata and a `mcp-shim` console script entry point
- `tests/` — a tiny import test to verify the package loads

Goals
-----
- Give you a runnable, editable package skeleton to plug in real resources, tools and prompts.
- Provide a small async server you can extend or replace with a real MCP protocol implementation.

Quick start (recommended)
-------------------------
1. Create and activate a virtualenv in the workspace root (if you haven't already):

```sh
python -m venv venv
. venv/bin/activate
```

2. Install the package in editable mode (inside the activated venv):

```sh
python -m pip install -U pip setuptools wheel
python -m pip install -e .
```

3. Run the server (in the activated venv):

```sh
mcp-shim --host 127.0.0.1 --port 31337
```

4. Probe the server from another terminal (newline-delimited JSON):

```sh
printf '{"type":"echo","payload":"hello"}\n' | nc 127.0.0.1 31337
```

Development
-----------
- Run tests (make sure the venv is activated):

```sh
python -m pytest -q
```

- Edit the server behaviour by overriding `MCPServer.on_request` or subclassing `MCPServer` in your app code.

Where to add your code
----------------------
- Resources: implement and register resource objects in `mcp/resources.py` or your own module and wire them into the server during startup.
- Tools: register callable tools with `ToolManager` and invoke them from `on_request`.
- Prompts: register templates and use `PromptManager.render` to build prompt strings.

VS Code tips
-----------
- The workspace contains a `.vscode/settings.json` snippet that attempts to start the integrated terminal with `bash` and auto-source `venv/bin/activate` if the venv exists. If you prefer to manage activation manually, remove or edit that setting.

Packaging & entry point
-----------------------
The package installs a console script called `mcp-shim` (configured in `pyproject.toml`), which maps to `mcp.__main__:main`.

Contributing
------------
- Add small, focused tests for new behaviour.
- If you change public APIs, update the examples and the README accordingly.

License
-------
MIT — see the `LICENSE` file.

Notes
-----
This repo is a scaffold. It is intentionally minimal so you can adapt the network protocol, message formats, auth, and runtime behaviour to your needs.

If you'd like, I can:
- Add an example resource + tool + prompt and show a small end-to-end request/response flow.
- Add CI (GitHub Actions) to run tests on push.
- Initialize a git repository and make an initial commit for you.

Tell me which of those you'd like next and I'll implement it.
