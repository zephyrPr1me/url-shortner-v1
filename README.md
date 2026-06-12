# FastAPI URL Shortener

A simple and efficient URL shortening API built with FastAPI, SQLAlchemy, and PostgreSQL.

## Features

- Create shortened URLs with unique identifiers
- Automatic URL normalization (adds `https://` if missing)
- Duplicate URL detection
- Click tracking for each shortened URL
- Async database operations using PostgreSQL
- Automatic table creation on startup

## Tech Stack

- **FastAPI** - Web framework
- **SQLAlchemy 2.0** - ORM with async support
- **PostgreSQL** - Database
- **Uvicorn** - ASGI server
- **Ruff** - Linting and formatting

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Installation

1. Clone the repository:

```bash
git clone https://github.com/zephyrPr1me/url-shortner-v1.git
cd fastapi-url-shortner
```

2. Install dependencies using uv:

```bash
uv sync
```

## Usage

### Run the server

```bash
uv run python main.py
```

Or with uvicorn directly:

```bash
uv run uvicorn main:app --reload --host localhost --port 8000
```

Run with Docker Compose:

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

### API Endpoints

#### Home

```
GET /
```

Returns a welcome message.

#### Shorten URL

```
POST /shorten
```

Request body:
```json
{
  "target_url": "https://example.com/some-long-url"
}
```

Response:
```json
{
  "target_url": "https://example.com/some-long-url",
  "short_id": "aB3cD4eF5gH6",
  "clicks": 0,
  "created_at": "2026-04-11T12:00:00"
}
```

#### Redirect to Original URL

```
GET /{short_id}
```

Redirects to the original URL and increments the click counter.

### Interactive Docs

FastAPI provides automatic interactive API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
fastapi-url-shortner/
├── app/
│   ├── main.py            # FastAPI app and route handlers
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── core/
│   │   ├── config.py      # application settings
│   │   └── database.py    # database engine and session
├── docker-compose.yml     # local service composition with PostgreSQL
├── pyproject.toml         # project dependencies
└── .gitignore             # git ignore rules
```

## Development

### Run linting

```bash
uv run ruff check .
```

### Format code

```bash
uv run ruff format .
```

## License

MIT License - See [LICENSE](LICENSE) file for details
