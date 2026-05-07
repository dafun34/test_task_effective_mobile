# Используем официальный образ Python
FROM python:3.12-slim
ENV PYTHONUNBUFFERED "1"

# Устанавливаем рабочую директорию
ENV PYTHONPATH "/code"
WORKDIR /code

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*


# Синхронизируем зависимости через uv
COPY ./pyproject.toml .
RUN pip install uv && uv pip install . --system

COPY ./app ./app
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
