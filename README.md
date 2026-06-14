# FastAPI URL Shortener

A simple, async URL shortening API built with FastAPI, SQLAlchemy 2.0, and PostgreSQL.

**Features:** URL shortening, click tracking, auto-normalization, duplicate detection, rate limiting, self-shortening protection.  
**Stack:** FastAPI, SQLAlchemy (async), PostgreSQL, Alembic, Uvicorn, slowapi, Ruff.

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

## 🔒 Security

### Rate Limiting
The `POST /shorten` endpoint is limited to **10 requests per minute** per IP address.  
Exceeding this limit returns `429 Too Many Requests`.

### Self-Shortening Protection
Attempting to shorten a URL that points back to this service itself is blocked with `400 Bad Request`.  
Configure the service base URL via the `BASE_URL` environment variable:

```env
BASE_URL=https://your-domain.com
```

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | *(auto-built)* | Full async PostgreSQL DSN |
| `POSTGRES_USER` | `myuser` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `mysecretpassword123` | PostgreSQL password |
| `POSTGRES_DB` | `mydatabase` | PostgreSQL database name |
| `POSTGRES_HOST` | `postgres` | PostgreSQL host |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `BASE_URL` | `http://localhost:8000` | Public base URL of this service (used for self-shortening protection) |
| `DB_ECHO` | `false` | Log all SQL queries |

## 🛠️ Code Quality

```bash
uv run ruff check . --fix  # Lint & auto-fix
uv run ruff format .       # Format code
```

## 🧪 Testing

```bash
uv run pytest
```

Tests use an in-memory SQLite database and cover: URL shortening, redirect, click tracking, validation, duplicate detection, rate limiting, and self-shortening protection.

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.
