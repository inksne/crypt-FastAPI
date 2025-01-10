from fastapi import APIRouter, HTTPException
from starlette import status

import httpx

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