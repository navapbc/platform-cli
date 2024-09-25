FROM python:3.11-slim

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-dev

COPY platform /app/platform

ENTRYPOINT ["poetry", "run", "python", "-m", "platform.cli"]
