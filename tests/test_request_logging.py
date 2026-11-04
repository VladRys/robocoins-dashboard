import asyncio
from types import SimpleNamespace

from fastapi.responses import JSONResponse

from app.main import log_http_requests


def test_client_error_log_includes_request_details(caplog):
    async def run():
        request = SimpleNamespace(
            headers={},
            state=SimpleNamespace(),
            method="GET",
            url=SimpleNamespace(path="/daily/25/daily-task/answer"),
        )

        async def call_next(_request):
            return JSONResponse(status_code=409, content={"detail": "Already completed"})

        await log_http_requests(request, call_next)

    with caplog.at_level("WARNING", logger="app.main"):
        asyncio.run(run())

    assert "GET /daily/25/daily-task/answer returned 409" in caplog.text
    assert "request_id=" in caplog.text
