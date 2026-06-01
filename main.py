import os
from datetime import datetime
from zoneinfo import ZoneInfo

from fastmcp import FastMCP


TOKYO_TZ = ZoneInfo("Asia/Tokyo")

mcp = FastMCP(
    name="long-mcp",
    instructions="MCP server exposing local time tools for Tokyo, Japan.",
)


@mcp.tool
def get_tokyo_time() -> dict[str, str]:
    """Return the current local time in Tokyo, Japan (UTC+09:00)."""
    now = datetime.now(TOKYO_TZ)
    return {
        "timezone": "Asia/Tokyo",
        "utc_offset": now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:],
        "iso8601": now.isoformat(timespec="seconds"),
        "date": now.date().isoformat(),
        "time": now.strftime("%H:%M:%S"),
        "weekday": now.strftime("%A"),
    }


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "stdio":
        mcp.run(transport=transport)
        return

    mcp.run(
        transport=transport,
        host=os.getenv("MCP_HOST", "127.0.0.1"),
        port=int(os.getenv("MCP_PORT", "8000")),
    )


if __name__ == "__main__":
    main()
