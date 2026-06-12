import secrets
import string
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from app.core.config import settings
from app.core.database import get_session
from app.models import URLModel, create_tables
from app.schemas import URLCreate, URLResponse
from app.utils.url_check import (
    check_url_domain_zone,
    check_url_format,
    check_url_length,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)

Session = Annotated[AsyncSession, Depends(get_session)]


@app.get("/")
async def home():
    return {"message": "Welcome to the URL Shortener API!"}


def generate_short_id(length: int = 6):
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


async def get_url_by_short_id(short_id: str, session: AsyncSession):
    result = await session.execute(
        select(URLModel).where(URLModel.short_id == short_id)
    )
    return result.scalar_one_or_none()


async def duplicate_url_check(target_url: str, session: AsyncSession):
    result = await session.execute(
        select(URLModel).where(URLModel.original_url == target_url)
    )
    return result.scalar_one_or_none()


@app.post("/shorten", response_model=URLResponse)
async def shorten_url(url: URLCreate, session: Session):
    normalized_url = url.target_url
    if not check_url_format(normalized_url):
        normalized_url = "https://" + normalized_url

    if not check_url_length(normalized_url):
        raise HTTPException(status_code=400, detail="URL is too long")

    if not check_url_domain_zone(normalized_url, settings.ALLOWED_DOMAINS):
        raise HTTPException(status_code=400, detail="URL domain not allowed")

    if await duplicate_url_check(normalized_url, session):
        raise HTTPException(status_code=400, detail="URL already exists")

    short_id = generate_short_id(12)
    while await get_url_by_short_id(short_id, session):
        short_id = generate_short_id(12)

    new_object = URLModel(original_url=normalized_url, short_id=short_id)
    session.add(new_object)
    await session.commit()
    await session.refresh(new_object)
    return {
        "target_url": new_object.original_url,
        "short_id": new_object.short_id,
        "clicks": new_object.clicks,
        "created_at": new_object.created_at,
    }


@app.get("/{short_id}")
async def redirect_url(short_id: str, session: Session):
    url = await get_url_by_short_id(short_id, session)
    if url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    url.clicks += 1
    await session.commit()
    return RedirectResponse(url=url.original_url)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)
