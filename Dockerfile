# app/Dockerfile

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y wget unzip && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install poetry

COPY pyproject.toml /app

ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV VIRTUAL_ENVIRONMENT_PATH="/app/.venv"
ENV PATH="$VIRTUAL_ENVIRONMENT_PATH/bin:$PATH"

RUN poetry install --no-interaction --only=main

# root-less image
RUN groupadd -g 1001 app && useradd -r -u 1001 -g app app -d /app

RUN chown -R app:app /app

COPY . /app

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

USER 1001

ENTRYPOINT ["./entrypoint.sh"]