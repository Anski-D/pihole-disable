# Use a Python image with uv pre-installed
ARG PYTHON_VERSION=3.13
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-trixie-slim

# Setup a non-root user
ARG UID=10001
RUN groupadd --system --gid "${UID}" nonroot \
 && useradd --system --gid "${UID}" --uid "${UID}" --create-home nonroot

# Install the project into `/app`
WORKDIR /app

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Prepare a logs directory
RUN ["mkdir", "logs"]
RUN chown "${UID}:${UID}" "logs"
RUN ["touch", ".docker"]

# Use the non-root user to run our application
USER nonroot

# Run the application
CMD ["hypercorn", "pihole_disable.main:app", "-b", "0.0.0.0:8888"]