from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session, get_session

Session = Annotated[AsyncSession, Depends(get_session)]


async def get_session_maker():
    return async_session
