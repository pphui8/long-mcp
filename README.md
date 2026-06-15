# long-mcp

MCP server exposing tools for local Tokyo, Japan time and server status.

## Run

```sh
uv run python main.py
```

## Tools

- `get_tokyo_time`: returns the current local time in Tokyo, Japan (`Asia/Tokyo`, UTC+09:00), including ISO 8601 timestamp, date, time, and weekday.
- `get_server_status`: returns read-only status for the server hosting this MCP web service, including process liveness, host/platform details, uptime, CPU count, load averages when available, and total memory when available.

`get_server_status` is administrator-only by tool-use policy. LLM clients should invoke it only when the user explicitly denotes that they are the administrator or clearly states an administrator role. If the user asks for server status without mentioning that role, ask for administrator confirmation first instead of invoking the tool.
