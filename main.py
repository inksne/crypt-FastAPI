from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette import status

from pydantic import BaseModel

from database.database import create_db_and_tables, get_async_session
from database.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from auth.auth import router as auth_router
from auth.utils import hash_password
from exchange_rate import router as crypt_router
from templates.router import router as template_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title='Crypt')


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserResponse(BaseModel):
    id: int
    email: str
    username: str


@app.post('/register', response_model=UserResponse)
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        hashed_password = hash_password(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password, email=email)

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return RedirectResponse('/jwt/login/', status_code=status.HTTP_303_SEE_OTHER)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Данное имя пользователя уже используется. Попробуйте другое.')


app.include_router(auth_router)
app.include_router(crypt_router)
app.include_router(template_router)