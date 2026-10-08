from fastapi import BackgroundTasks, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import desc, select

from app.core.config import settings
from app.core.session import AsyncSession, Session
from app.models import URLModel
from app.schemas import URLCreate
from app.utils.util import (
    check_self_shortening,
    check_url_length,
    generate_short_id,
    is_valid_url,
)


async def get_url_by_short_id(short_id: str, session: AsyncSession):
    result = await session.execute(
        select(URLModel).where(URLModel.short_id == short_id)
    )
    return result.scalar_one_or_none()


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


async def increment_clicks(short_id: str, session: AsyncSession):
    url = await get_url_by_short_id(short_id, session)
    if url:
        url.clicks += 1
        await session.commit()


async def redirect_url(
    short_id: str,
    session: Session,
    tasks: BackgroundTasks,
):
    url = await get_url_by_short_id(short_id, session)
    if url is None:
        raise HTTPException(status_code=404, detail="URL not found")

    tasks.add_task(increment_clicks, short_id, session)
    return RedirectResponse(url=url.original_url)


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


async def duplicate_url_check(target_url: str, session: AsyncSession):
    result = await session.execute(
        select(URLModel).where(URLModel.original_url == target_url)
    )
    return result.scalar_one_or_none()
