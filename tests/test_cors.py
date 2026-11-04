import asyncio

from app.core.config import prod_cors_origins
from app.main import app


def test_prod_cors_origins_normalizes_bare_hosts(monkeypatch):
    monkeypatch.setenv(
        "PROD_CORS_ORIGINS",
        "robocoins.tech, localhost:5500, https://dashboard.example.com/",
    )

    assert prod_cors_origins() == [
        "https://robocoins.tech",
        "http://localhost:5500",
        "https://dashboard.example.com",
    ]


def test_localhost_preflight_allows_credentials():
    async def run_test():
        messages = []

        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message):
            messages.append(message)

        await app(
            {
                "type": "http",
                "asgi": {"version": "3.0"},
                "http_version": "1.1",
                "method": "OPTIONS",
                "scheme": "http",
                "path": "/auth/login",
                "raw_path": b"/auth/login",
                "query_string": b"",
                "headers": [
                    (b"origin", b"http://localhost:5173"),
                    (b"access-control-request-method", b"POST"),
                    (b"access-control-request-headers", b"content-type"),
                ],
                "server": ("localhost", 8000),
                "client": ("localhost", 5173),
                "root_path": "",
            },
            receive,
            send,
        )

        response = next(
            message for message in messages if message["type"] == "http.response.start"
        )
        headers = dict(response["headers"])
        assert response["status"] == 200
        assert headers[b"access-control-allow-origin"] == b"http://localhost:5173"
        assert headers[b"access-control-allow-credentials"] == b"true"

    asyncio.run(run_test())
