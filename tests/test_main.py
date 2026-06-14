import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.models import URLModel


@pytest.mark.asyncio
async def test_home(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the URL Shortener API!"}


@pytest.mark.asyncio
async def test_shorten_url_success(client: AsyncClient, db_session):
    payload = {"target_url": "https://google.com"}
    response = await client.post("/shorten", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["target_url"] == "https://google.com/"
    assert "short_id" in data
    assert data["clicks"] == 0
    assert "created_at" in data

    # Verify database entry exists
    stmt = select(URLModel).where(URLModel.short_id == data["short_id"])
    result = await db_session.execute(stmt)
    url_model = result.scalar_one_or_none()
    assert url_model is not None
    assert url_model.original_url == "https://google.com/"


@pytest.mark.asyncio
async def test_shorten_url_invalid_format(client: AsyncClient):
    # Pydantic HttpUrl validation will fail on non-URL format, returning 422
    payload = {"target_url": "invalid-url"}
    response = await client.post("/shorten", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_shorten_url_self_shortening(client: AsyncClient):
    """Shortening a link that points back to this service must be rejected."""
    # The test client's base_url is http://test, which maps to BASE_URL default.
    # We patch via the known host of the test client.
    payload = {"target_url": "http://localhost:8000/some-existing-path"}
    response = await client.post("/shorten", json=payload)
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_shorten_url_duplicate(client: AsyncClient):
    payload = {"target_url": "https://github.com"}

    # First request
    response1 = await client.post("/shorten", json=payload)
    assert response1.status_code == 200

    # Second request with same URL
    response2 = await client.post("/shorten", json=payload)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "URL already exists"


@pytest.mark.asyncio
async def test_shorten_url_rate_limiting(client: AsyncClient):
    """More than 10 requests per minute from same IP should return 429."""
    responses = []
    # First 10 should succeed (or 400 for duplicates after the first)
    # The 11th+ must be 429
    for i in range(12):
        r = await client.post(
            "/shorten",
            json={"target_url": f"https://example-rate-{i}.com"},
        )
        responses.append(r.status_code)

    assert 429 in responses, "Expected a 429 Too Many Requests response"


@pytest.mark.asyncio
async def test_redirect_and_click_tracking(client: AsyncClient, db_session):
    # Shorten a URL first
    payload = {"target_url": "https://news.ycombinator.com"}
    response = await client.post("/shorten", json=payload)
    data = response.json()
    short_id = data["short_id"]

    # Request the redirect (allow_redirects=False to inspect the 307)
    redirect_response = await client.get(f"/{short_id}", follow_redirects=False)
    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "https://news.ycombinator.com/"

    # Wait briefly for background task to execute click increment
    await asyncio.sleep(0.1)

    # Re-fetch from db to verify clicks incremented
    stmt = select(URLModel).where(URLModel.short_id == short_id)
    result = await db_session.execute(stmt)
    url_model = result.scalar()
    await db_session.refresh(url_model)
    assert url_model.clicks == 1


@pytest.mark.asyncio
async def test_redirect_not_found(client: AsyncClient):
    response = await client.get("/nonexistentid")
    assert response.status_code == 404
    assert response.json()["detail"] == "URL not found"
