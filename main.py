import os
import platform
import socket
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from fastmcp import FastMCP


TOKYO_TZ = ZoneInfo("Asia/Tokyo")
PROCESS_STARTED_AT = time.monotonic()
StatusValue = str | int | float | None

mcp = FastMCP(
    name="long-mcp",
    instructions=(
        "MCP server exposing local time tools for Tokyo, Japan and a server status tool. "
        "Only invoke get_server_status when the user explicitly denotes that they are "
        "the administrator or otherwise clearly states an administrator role. If the "
        "user asks for server status without mentioning that role, do not invoke the "
        "tool; ask them to confirm whether they are the administrator first."
    ),
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


def _host_uptime_seconds() -> float | None:
    try:
        with open("/proc/uptime", encoding="utf-8") as uptime_file:
            return float(uptime_file.read().split()[0])
    except (FileNotFoundError, IndexError, OSError, ValueError):
        return None


def _load_average() -> dict[str, float | None]:
    try:
        one_minute, five_minutes, fifteen_minutes = os.getloadavg()
    except (AttributeError, OSError):
        return {
            "load_average_1m": None,
            "load_average_5m": None,
            "load_average_15m": None,
        }

    return {
        "load_average_1m": round(one_minute, 2),
        "load_average_5m": round(five_minutes, 2),
        "load_average_15m": round(fifteen_minutes, 2),
    }


def _total_memory_bytes() -> int | None:
    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        physical_pages = os.sysconf("SC_PHYS_PAGES")
    except (AttributeError, OSError, ValueError):
        return None

    if not isinstance(page_size, int) or not isinstance(physical_pages, int):
        return None

    return page_size * physical_pages


@mcp.tool
def get_server_status() -> dict[str, StatusValue]:
    """
    Return current status for the server hosting this MCP web service.

    Admin-only tool-use instruction for LLM clients: invoke this tool only when
    the user explicitly denotes that they are the administrator or clearly states
    an administrator role. If the user's request does not mention that role, do
    not invoke this tool; ask for administrator confirmation first.
    """
    now = datetime.now(TOKYO_TZ)
    status: dict[str, StatusValue] = {
        "status": "running",
        "checked_at": now.isoformat(timespec="seconds"),
        "timezone": "Asia/Tokyo",
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python_version": sys.version.split()[0],
        "process_id": os.getpid(),
        "process_uptime_seconds": round(time.monotonic() - PROCESS_STARTED_AT, 2),
        "host_uptime_seconds": _host_uptime_seconds(),
        "cpu_count": os.cpu_count(),
        "total_memory_bytes": _total_memory_bytes(),
    }
    status.update(_load_average())
    return status


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "stdio":
        mcp.run(transport=transport)
        return

    mcp.run(
        transport=transport,
        host=os.getenv("MCP_HOST", "127.0.0.1"),
        port=int(os.getenv("MCP_PORT", "9002")),
    )


if __name__ == "__main__":
    main()
