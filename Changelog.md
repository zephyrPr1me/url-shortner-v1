# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive test suite in `tests/` covering API endpoints (`/`, `/shorten`, `/{short_id}`), duplicate detection, click tracking, and validation errors.
- GitHub Actions CI workflow (`.github/workflows/ci.yml`) to automatically check linting, code formatting, and run tests on push and pull request.
- Development dependencies (`pytest`, `pytest-asyncio`, `httpx`, `aiosqlite`) managed via `uv`.

### Fixed
- Fixed background task `increment_clicks` database session crash by passing a proper session maker dependency instead of a generator.
- Fixed `AttributeError` crash on `/shorten` endpoint by converting Pydantic V2 `HttpUrl` objects to strings before validation and database checks.
- Reformatted codebase using Ruff.

## [0.1.0] - 2026-06-12

### Added
- Initial implementation of the URL Shortener API built with FastAPI, SQLAlchemy 2.0 (async), and PostgreSQL.
- Database index on `short_id` and `original_url`.
- Domain zone validation using `domain_zones.txt`.
- Multi-stage Dockerfile and docker-compose configurations.
- Alembic database migration setup.
