FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY agenda ./agenda
COPY migracoes ./migracoes
COPY alembic.ini ./
RUN pip install . && useradd --create-home --uid 1000 app

USER app
EXPOSE 8000

# Aplica as migrações e sobe a API.
CMD ["sh", "-c", "alembic upgrade head && uvicorn agenda.principal:app --host 0.0.0.0 --port 8000"]
