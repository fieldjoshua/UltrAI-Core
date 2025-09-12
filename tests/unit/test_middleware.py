import pytest
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from starlette.testclient import TestClient


@pytest.fixture()
def app_with_security_headers():
    from app.middleware.security_headers_middleware import (
        setup_security_headers_middleware,
    )

    app = FastAPI()

    @app.get("/ping")
    def ping():
        return PlainTextResponse("pong")

    setup_security_headers_middleware(app)
    return app


@pytest.fixture()
def app_with_rate_limit():
    from app.middleware.rate_limit_middleware import setup_rate_limit_middleware

    app = FastAPI()

    @app.get("/ping")
    def ping():
        return PlainTextResponse("pong")

    setup_rate_limit_middleware(app)
    return app


@pytest.mark.unit
def test_security_headers_present(app_with_security_headers):
    client = TestClient(app_with_security_headers)
    r = client.get("/ping")
    assert r.status_code == 200
    assert "Content-Security-Policy" in r.headers
    assert r.headers["X-Frame-Options"] in {"DENY", "SAMEORIGIN"}
    assert r.headers["X-Content-Type-Options"].lower() == "nosniff"
    assert "Strict-Transport-Security" in r.headers


@pytest.mark.unit
def test_rate_limit_headers_present(app_with_rate_limit):
    client = TestClient(app_with_rate_limit)
    r = client.get("/ping")
    assert r.status_code == 200
    # Middleware adds headers; service may fall back if Redis unavailable
    assert "X-RateLimit-Limit" in r.headers
    assert "X-RateLimit-Remaining" in r.headers
    assert "X-RateLimit-Reset" in r.headers
