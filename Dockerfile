FROM ghcr.io/astral-sh/uv:python3.11-alpine3.23

WORKDIR /app

# Copy project files
COPY . .

# Sync dependencies (creates .venv)
RUN uv sync --locked --no-dev

# Activate the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Create workspace directory
RUN mkdir -p /yaml_workspace

# Run the application
ENTRYPOINT ["py-yaml-composer"]
CMD []
