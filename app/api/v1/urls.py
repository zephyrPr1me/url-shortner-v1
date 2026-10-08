from fastapi import APIRouter, BackgroundTasks, Request
from starlette.responses import FileResponse

from app.core.limiter import limiter
from app.core.session import Session
from app.crud.crud import list_urls
from app.crud.crud import redirect_url as redirect_url_handler
from app.crud.crud import shorten_url as shorten_url_handler
from app.schemas import URLCreate, URLResponse

router = APIRouter()


@router.get("/")
async def home():
    return FileResponse("app/static/index.html")


@router.get("/urls", response_model=list[dict])
async def list_urls_route(session: Session):
    return await list_urls(session)


@router.post("/shorten", response_model=URLResponse)
@limiter.limit("10/minute")
async def shorten_url(
    request: Request,
    url: URLCreate,
    session: Session,
):
    return await shorten_url_handler(request, url, session)


@router.get("/{short_id}")
async def redirect_url(
    short_id: str,
    session: Session,
    tasks: BackgroundTasks,
):
    return await redirect_url_handler(short_id, session, tasks)
