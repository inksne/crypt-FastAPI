from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect

import pytest
import json

from main import app

client = TestClient(app)


def test_read_main_page():
    response = client.get('/')
    assert response.status_code == 200


def test_read_about_us_page():
    response = client.get('/about_us')
    assert response.status_code == 200


def test_read_register_page():
    response = client.get('/jwt/register')
    assert response.status_code == 200


def test_read_login_page():
    response = client.get('/jwt/login')
    assert response.status_code == 200


def test_login_user():
    response = client.post(
        "/jwt/login/",
        data={"username": "inksne", "password": "ink"},
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens


def test_refresh_token():
    login_response = client.post(
        "/jwt/login/",
        data={"username": "inksne", "password": "ink"},
    )
    refresh_token = login_response.json()["refresh_token"]
    
    response = client.post(
        "/jwt/refresh/",
        cookies={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_logout():
    response = client.post("/jwt/logout")
    assert response.status_code == 200
    assert response.json() == {"detail": "Успешный выход"}


def test_fetch_crypto_details():
    response = client.get("/crypt/BTCUSDT")
    try:
        assert response.status_code == 200
        assert "<html" in response.text
        assert "BTCUSDT" in response.text
    except AssertionError:
        assert response.status_code == 404


def test_websocket_prices():
    with client.websocket_connect("/ws/crypt_prices") as websocket:
        try:
            message = websocket.receive_text()
            prices = json.loads(message)
            assert isinstance(prices, dict)
        except WebSocketDisconnect:
            pytest.fail("WebSocket disconnected unexpectedly")
