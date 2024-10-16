FROM python:3.11-slim

RUN pip install poetry

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

ENTRYPOINT ["poetry", "run", "nava-platform"]
