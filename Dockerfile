# Make sure PYTHON_VERSION matches the value in .python-version
# renovate: datasource=python-version depName=python
ARG PYTHON_VERSION=3.12

FROM ghcr.io/astral-sh/uv:python$PYTHON_VERSION-trixie-slim@sha256:0130b1999b49c28d1d9a2a20793825e5ea6b808be1036e979d654196e3c7dc86 

# allow all users to get into "home", like git checking for a global ignore
# file, until better user juggling in the future
RUN chmod -R 777 /root

RUN apt-get update \
 && apt-get install --no-install-recommends --yes \
       git
RUN git config --global --add safe.directory "*"

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_SYSTEM_PYTHON=true

WORKDIR /app

RUN touch README.md
COPY pyproject.toml uv.lock /app/
# install the project's dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# then the project itself
COPY nava /app/nava
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

COPY bin/docker-entry /usr/local/bin

WORKDIR /project-dir
ENTRYPOINT ["docker-entry"]
