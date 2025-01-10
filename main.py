from fastapi import FastAPI, Form, Depends
from contextlib import asynccontextmanager

from pydantic import BaseModel

from database.database import create_db_and_tables, get_async_session
from database.models import User
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import router as auth_router
from auth.utils import hash_password
from exchange_rate import router as crypt_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title='Crypt')


class UserResponse(BaseModel):
    id: int
    email: str
    username: str


@app.get('/')
async def base():
    return {'detail': 'Hello, World!'}


@app.post('/register', response_model=UserResponse)
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_async_session)
):
    hashed_password = hash_password(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password, email=email)

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


app.include_router(auth_router)
app.include_router(crypt_router)