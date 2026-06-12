FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Копируем только файлы зависимостей для кэширования слоя
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости в виртуальное окружение
# --frozen означает "использовать строго версии из uv.lock"
RUN uv sync --frozen --no-install-project

# Копируем исходный код
COPY . .

# Устанавливаем сам проект (если нужно)
RUN uv sync --frozen

# Финальный этап (можно использовать тот же образ или более легкий)
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Копируем виртуальное окружение и код из builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

# Добавляем venv в PATH
ENV PATH="/app/.venv/bin:$PATH"

# Запуск приложения
CMD ["uv", "run", "fastapi", "run", "main.py"]
