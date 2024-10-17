FROM python:3.11-slim

# allow all users to get into "home", like git checking for a global ignore
# file, until better user juggling in the future
RUN chmod -R 777 /root

RUN pip install poetry
RUN apt-get update \
 && apt-get install --no-install-recommends --yes \
       git
RUN git config --global --add safe.directory "*"

ENV POETRY_NO_INTERACTION=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

RUN touch README.md
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

COPY nava /app/nava
RUN poetry install --only-root
RUN ln -sf /app/.venv/bin/nava-platform /usr/local/bin/

COPY bin/docker-entry /usr/local/bin

WORKDIR /project-dir
ENTRYPOINT ["docker-entry"]
