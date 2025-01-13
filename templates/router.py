from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

import logging


router = APIRouter(tags=['Templates'])

templates = Jinja2Templates(directory='templates')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get('/about_us', response_class=HTMLResponse)
async def get_base_page(request: Request):
    return templates.TemplateResponse(request, 'about_us.html')


@router.get('/jwt/register', response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse(request, 'register.html')


@router.get('/jwt/login/', response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse(request, 'login.html')


@router.get('/authenticated/', response_class=HTMLResponse)
async def get_auth_page(request: Request):
    return templates.TemplateResponse(request, 'auth_index.html')