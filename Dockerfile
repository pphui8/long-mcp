FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV MCP_TRANSPORT=streamable-http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=9002

COPY . .
RUN uv sync --frozen --no-dev

EXPOSE 9002

CMD ["uv", "run", "python", "main.py"]
