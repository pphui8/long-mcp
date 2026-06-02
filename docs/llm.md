# long-mcp LLM Handoff

## Project Summary

`long-mcp` is a small Python MCP server built with FastMCP. It exposes tools for retrieving local Tokyo, Japan time data.

The current project has one MCP tool:

- `get_tokyo_time`: returns the current time in the `Asia/Tokyo` timezone.

## System Architecture

The project is intentionally minimal:

- `main.py` defines the FastMCP server, registers tools, and starts the server.
- `pyproject.toml` declares Python package metadata and dependencies.
- `Dockerfile` defines the container runtime used for deployment.
- `README.md` gives a short user-facing summary.
- `docs/llm.md` provides this project handoff for future LLMs and maintainers.

Runtime architecture:

1. A `FastMCP` instance named `long-mcp` is created in `main.py`.
2. Python functions decorated with `@mcp.tool` become MCP-callable tools.
3. `main()` reads transport configuration from environment variables.
4. The MCP server starts either over `stdio` or an HTTP transport.

## APIs

### MCP Tools

#### `get_tokyo_time`

Signature:

```python
def get_tokyo_time() -> dict[str, str]
```

Description:

Returns the current local time in Tokyo, Japan.

Inputs:

- None.

Output fields:

- `timezone`: Always `Asia/Tokyo`.
- `utc_offset`: Current UTC offset, formatted like `+09:00`.
- `iso8601`: ISO 8601 timestamp with seconds precision.
- `date`: Local date in `YYYY-MM-DD` format.
- `time`: Local time in `HH:MM:SS` format.
- `weekday`: English weekday name.

Example response:

```json
{
  "timezone": "Asia/Tokyo",
  "utc_offset": "+09:00",
  "iso8601": "2026-06-02T12:34:56+09:00",
  "date": "2026-06-02",
  "time": "12:34:56",
  "weekday": "Tuesday"
}
```

## Available Functionalities

Current functionality:

- Report Tokyo local time.
- Report Tokyo local date.
- Report Tokyo UTC offset.
- Report Tokyo weekday.
- Run as an MCP server over `stdio`.
- Run as an MCP server over Streamable HTTP when configured through environment variables or Docker.

Not currently implemented:

- Time lookup for arbitrary cities or timezones.
- Authentication or authorization.
- Persistent storage.
- External API integrations.
- Multiple MCP resources or prompts.
- Health-check endpoint implemented in application code.

## Runtime Configuration

`main.py` reads these environment variables:

- `MCP_TRANSPORT`: MCP transport. Defaults to `stdio`.
- `MCP_HOST`: Host bind address for non-stdio transports. Defaults to `127.0.0.1`.
- `MCP_PORT`: Port for non-stdio transports. Defaults to `9002`.

Docker defaults:

- `MCP_TRANSPORT=streamable-http`
- `MCP_HOST=0.0.0.0`
- `MCP_PORT=9002`

The Docker image exposes port `9002`.

## Local Development

Run locally with the default `stdio` transport:

```sh
uv run python main.py
```

Run locally over Streamable HTTP:

```sh
MCP_TRANSPORT=streamable-http MCP_HOST=127.0.0.1 MCP_PORT=9002 uv run python main.py
```

Expected HTTP MCP endpoint:

```text
http://127.0.0.1:9002/mcp
```

## Deployment Notes

The `Dockerfile` uses:

- Base image: `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`
- Dependency install: `uv sync --frozen --no-dev`
- Entrypoint: `uv run python main.py`

When deployed in Docker, connect MCP clients to:

```text
http://<server-host>:9002/mcp
```

If the service is behind a reverse proxy, the externally visible URL may be different, for example:

```text
https://<domain>/mcp
```

## Testing Guidance

Use a FastMCP client to validate the deployed server:

```python
import asyncio
from fastmcp import Client

MCP_URL = "http://127.0.0.1:9002/mcp"

async def main():
    async with Client(MCP_URL) as client:
        tools = await client.list_tools()
        result = await client.call_tool("get_tokyo_time", {})
        print(tools)
        print(result)

asyncio.run(main())
```

Validation checklist:

- The server process starts without exceptions.
- The MCP client can connect to `/mcp`.
- `list_tools()` includes `get_tokyo_time`.
- Calling `get_tokyo_time` returns a dictionary with the expected fields.
- `timezone` is `Asia/Tokyo`.
- `utc_offset` is `+09:00`.

## Extension Guidance

To add a new tool:

1. Define a normal Python function in `main.py`.
2. Decorate it with `@mcp.tool`.
3. Use explicit type annotations for inputs and outputs.
4. Add a docstring describing what the tool does.
5. Update `README.md` and this file with the new tool contract.

Example pattern:

```python
@mcp.tool
def example_tool(input_value: str) -> dict[str, str]:
    """Describe what the tool returns."""
    return {"value": input_value}
```

Keep new functionality small and explicit unless the project grows enough to justify splitting tools into separate modules.
