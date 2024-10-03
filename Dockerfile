FROM python:3.11-slim

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-dev

COPY nava /app/nava

ENTRYPOINT ["poetry", "run", "python", "-m", "nava.cli"]
