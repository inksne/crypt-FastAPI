from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocket, WebSocketDisconnect
from starlette import status

import httpx
import asyncio
import json
from redis import Redis

from templates.router import templates

router = APIRouter(tags=['Crypt'])

redis = Redis(host='127.0.0.1', port=6379, db=0)


async def save_price_in_redis(symbol: str, price: float, status: str):
    timestamp = int(asyncio.get_event_loop().time())
    redis.zadd(symbol, {timestamp: price})
    # Save status too
    redis.set(f"{symbol}_status", status)


@router.get('/crypt')
async def fetch_price(symbol: str):
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {"symbol": symbol}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()["price"]
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Валюта не найдена.')
        

async def fetch_prices():
    symbols = [
        "BTCUSDT",
        "ETHUSDT",
        "BNBUSDT",
        "AIXBTUSDT",
        "CGPTUSDT",
        "COOKIEUSDT",
        "TFUELUSDT",
        "AVAXUSDT",
        "SOLUSDT"
    ]
    url = "https://api.binance.com/api/v3/ticker/price"
    prices = {}

    async with httpx.AsyncClient() as client:
        for symbol in symbols:
            params = {"symbol": symbol}
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                price = response.json().get("price", "0")
                trend = "растёт" if float(price) > 100 else "падает"
                prices[symbol] = {"price": price, "status": trend}
                await save_price_in_redis(symbol, price, trend)
            except httpx.HTTPStatusError:
                prices[symbol] = {"price": "Error", "status": "стабильно"}

    return prices


@router.get("/crypt/{symbol}")
async def get_crypto_details(request: Request, symbol: str):
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {"symbol": symbol}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            price = response.json().get("price")
            if not price:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Криптовалюта не найдена")

            crypto_data = {
                "symbol": symbol,
                "price": price,
            }

            return templates.TemplateResponse("crypto_details.html", {"request": request, "crypto": crypto_data})
        
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Криптовалюта не найдена")


@router.get('/', response_class=HTMLResponse)
async def get_base_page(request: Request):
    return templates.TemplateResponse(request, 'index.html')


@router.websocket("/ws/crypt_prices")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                prices = await fetch_prices()
                await websocket.send_text(json.dumps(prices))
            except RuntimeError:
                break
            except Exception as e:
                await websocket.send_text(json.dumps({"error": str(e)}))
    except RuntimeError:
        pass
    except WebSocketDisconnect:
        raise HTTPException(status_code=status.WS_1000_NORMAL_CLOSURE)