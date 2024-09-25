# Step 1: Use an official Python image
FROM python:3.11-slim

# Step 2: Install poetry
RUN pip install poetry

# Step 3: Set the working directory
WORKDIR /platform

# Step 4: Copy the poetry files and install dependencies
COPY pyproject.toml poetry.lock* /platform/
RUN poetry install --no-dev

# Step 5: Copy the source code
COPY platform /platform

# Step 6: Set the default command to run the CLI
CMD ["poetry", "run", "python", "-m", "platform.cli"]
