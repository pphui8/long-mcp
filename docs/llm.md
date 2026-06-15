# long-mcp LLM Handoff

## Project Summary

`long-mcp` is a small Python MCP server built with FastMCP. It exposes tools for retrieving local Tokyo, Japan time data and read-only server status data.

The current project has two MCP tools:

- `get_tokyo_time`: returns the current time in the `Asia/Tokyo` timezone.
- `get_server_status`: returns current status for the server hosting this MCP web service.

Tool-use policy:

- `get_server_status` is administrator-only by policy. LLM clients should invoke it only when the user explicitly denotes that they are the administrator or clearly states an administrator role.
- If the user asks for server status without mentioning an administrator role, do not invoke `get_server_status`; ask them to confirm whether they are the administrator first.

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

#### `get_server_status`

Signature:

```python
def get_server_status() -> dict[str, str | int | float | None]
```

Description:

Returns current read-only status for the server hosting this MCP web service.

Admin-only invocation rule:

- Invoke this tool only when the user explicitly denotes that they are the administrator or clearly states an administrator role.
- If the user asks for server status without mentioning that role, ask for administrator confirmation first instead of invoking the tool.

Inputs:

- None.

Output fields:

- `status`: Service status string. Currently `running` when the tool responds.
- `checked_at`: ISO 8601 timestamp with seconds precision in `Asia/Tokyo`.
- `timezone`: Always `Asia/Tokyo`.
- `hostname`: Hostname reported by the operating system.
- `platform`: Operating system platform string.
- `python_version`: Runtime Python version.
- `process_id`: Current MCP server process ID.
- `process_uptime_seconds`: Seconds since this Python process started.
- `host_uptime_seconds`: Host uptime in seconds when available, otherwise `null`.
- `cpu_count`: Logical CPU count when available, otherwise `null`.
- `total_memory_bytes`: Total physical memory in bytes when available, otherwise `null`.
- `load_average_1m`: 1-minute host load average when available, otherwise `null`.
- `load_average_5m`: 5-minute host load average when available, otherwise `null`.
- `load_average_15m`: 15-minute host load average when available, otherwise `null`.

Example response:

```json
{
  "status": "running",
  "checked_at": "2026-06-02T12:34:56+09:00",
  "timezone": "Asia/Tokyo",
  "hostname": "web-01",
  "platform": "Linux-6.1.0-x86_64-with-glibc2.36",
  "python_version": "3.12.11",
  "process_id": 1234,
  "process_uptime_seconds": 85.42,
  "host_uptime_seconds": 452918.25,
  "cpu_count": 4,
  "total_memory_bytes": 8589934592,
  "load_average_1m": 0.15,
  "load_average_5m": 0.2,
  "load_average_15m": 0.18
}
```

## Available Functionalities

Current functionality:

- Report Tokyo local time.
- Report Tokyo local date.
- Report Tokyo UTC offset.
- Report Tokyo weekday.
- Report read-only server status for administrator-denoted requests.
- Run as an MCP server over `stdio`.
- Run as an MCP server over Streamable HTTP when configured through environment variables or Docker.

Not currently implemented:

- Time lookup for arbitrary cities or timezones.
- Enforced authentication or authorization. `get_server_status` relies on LLM tool-use instructions and client behavior; it does not verify identity in application code.
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
- `list_tools()` includes `get_tokyo_time` and `get_server_status`.
- Calling `get_tokyo_time` returns a dictionary with the expected fields.
- `timezone` is `Asia/Tokyo`.
- `utc_offset` is `+09:00`.
- Calling `get_server_status` after administrator confirmation returns `status` as `running`.
- LLM clients should not call `get_server_status` unless the user explicitly denotes that they are the administrator or clearly states an administrator role.

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
