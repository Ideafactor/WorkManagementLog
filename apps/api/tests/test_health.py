"""Application liveness contract tests."""

from http import HTTPStatus

import pytest
from app.main import create_app
from httpx import ASGITransport, AsyncClient


@pytest.mark.anyio
async def test_health_is_database_independent() -> None:
    """A running process reports liveness without requiring PostgreSQL."""
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}
