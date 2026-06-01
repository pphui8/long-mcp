FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV MCP_TRANSPORT=streamable-http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=9000

COPY . .
RUN uv sync --frozen --no-dev

EXPOSE 9000

CMD ["uv", "run", "python", "main.py"]
