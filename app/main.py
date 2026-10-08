import secrets
import string
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse, FileResponse

from app.core.config import settings
from app.core.database import async_session, get_session
from app.models import URLModel
from app.schemas import URLCreate, URLResponse
from app.utils.url_check import (
    is_valid_url,
    check_url_length,
    check_self_shortening,
)

# ---------------------------------------------------------------------------
# Rate limiter — keyed by client IP
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address, default_limits=[])


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

Session = Annotated[AsyncSession, Depends(get_session)]


async def get_session_maker():
    return async_session


@app.get("/")
async def home():
    return FileResponse("app/static/index.html")


@app.get("/urls")
async def list_urls(session: Session):
    result = await session.execute(
        select(URLModel).order_by(desc(URLModel.created_at)).limit(20)
    )
    urls = result.scalars().all()
    if urls:
        return [
            {
                "target_url": url.original_url,
                "short_id": url.short_id,
                "clicks": url.clicks,
                "created_at": url.created_at.isoformat(),
            }
            for url in urls
        ]
    else:
        return {}


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
@limiter.limit("10/minute")
async def shorten_url(request: Request, url: URLCreate, session: Session):
    normalized_url = str(url.target_url)

    if not is_valid_url(normalized_url):
        raise HTTPException(status_code=400, detail="Invalid URL structure")

    if not check_url_length(normalized_url):
        raise HTTPException(status_code=400, detail="URL is too long")

    if check_self_shortening(normalized_url, settings.BASE_URL):
        raise HTTPException(
            status_code=400,
            detail="Shortening links that point to this service is not allowed",
        )

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


async def increment_clicks(short_id: str, session_maker):
    async with session_maker() as session:
        url = await get_url_by_short_id(short_id, session)
        if url:
            url.clicks += 1
            await session.commit()


@app.get("/{short_id}")
async def redirect_url(
    short_id: str,
    session: Session,
    tasks: BackgroundTasks,
    session_maker=Depends(get_session_maker),
):
    url = await get_url_by_short_id(short_id, session)
    if url is None:
        raise HTTPException(status_code=404, detail="URL not found")

    tasks.add_task(increment_clicks, short_id, session_maker)
    return RedirectResponse(url=url.original_url)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)
