from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocket, WebSocketDisconnect
from starlette import status

import httpx
import asyncio
import json

from templates.router import templates

router = APIRouter(tags=['Crypt'])

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
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT"]
    url = "https://api.binance.com/api/v3/ticker/price"
    prices = {}

    async with httpx.AsyncClient() as client:
        for symbol in symbols:
            params = {"symbol": symbol}
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                price = response.json().get("price", "0")
                prices[symbol] = price
            except httpx.HTTPStatusError:
                prices[symbol] = "Error"

    return prices


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
                await asyncio.sleep(10)
            except RuntimeError:
                break
            except Exception as e:
                await websocket.send_text(json.dumps({"error": str(e)}))
    except RuntimeError:
        pass
    except WebSocketDisconnect:
        pass