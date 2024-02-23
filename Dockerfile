FROM python:3.11 AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

ENV PATH="/app/.venv/bin:$PATH"

# Stage/Builder
FROM base AS stage

WORKDIR /app
RUN pip install poetry

COPY pyproject.toml poetry.lock /app/

RUN poetry install --only=main

COPY . /app/

# Production
FROM base AS prod
WORKDIR /app
COPY --from=stage /app /app

ENTRYPOINT ["./entrypoint.sh"]