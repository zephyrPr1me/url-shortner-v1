# FastAPI URL Shortener

A simple, async URL shortening API built with FastAPI, SQLAlchemy 2.0, and PostgreSQL.

**Features:** URL shortening, click tracking, auto-normalization, duplicate detection.  
**Stack:** FastAPI, SQLAlchemy (async), PostgreSQL, Alembic, Uvicorn, Ruff.

## 🚀 Quick Start (Docker)

The easiest way to run the app with PostgreSQL:

```bash
docker compose up --build
```
- **API:** `http://localhost:8000`
- **Swagger UI:** `http://localhost:8000/docs`

## 💻 Local Development

Requires Python 3.12+ and [uv](https://github.com/astral-sh/uv).

```bash
# Install dependencies
uv sync

# Run the server
uv run uvicorn app.main:app --reload
```

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Welcome message |
| `POST` | `/shorten` | Create a short URL (Body: `{"target_url": "..."}`) |
| `GET` | `/{short_id}` | Redirect to original URL & track clicks |
| `GET` | `/docs` | Interactive Swagger UI |

## 🛠️ Code Quality

```bash
uv run ruff check . --fix  # Lint & auto-fix
uv run ruff format .       # Format code
```

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.


