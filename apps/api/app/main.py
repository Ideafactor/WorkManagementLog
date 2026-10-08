"""FastAPI application and same-origin SPA entry point."""

from pathlib import Path
from typing import ClassVar, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text
from starlette.staticfiles import StaticFiles

from app.admin import router as admin_router
from app.auth.router import router as auth_router
from app.config import get_settings
from app.database.session import get_session_factory
from app.observability import StructuredAccessMiddleware


class HealthResponse(BaseModel):
    """Process or dependency health response."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)
    status: Literal["ok", "unavailable"]


def error_response(status_code: int, code: str) -> JSONResponse:
    """Return the shared error envelope."""
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": code, "field": None}},
    )


def create_app(static_dir: Path | None = None) -> FastAPI:
    """Build the API and optional SPA host."""
    settings = get_settings()
    application = FastAPI(title="Company Web API", version="0.1.0")
    application.add_middleware(StructuredAccessMiddleware)

    @application.exception_handler(HTTPException)
    async def handle_http(_request: Request, exception: HTTPException) -> JSONResponse:
        return error_response(exception.status_code, str(exception.detail))

    @application.exception_handler(RequestValidationError)
    async def handle_validation(
        _request: Request, _exception: RequestValidationError
    ) -> JSONResponse:
        return error_response(422, "VALIDATION_ERROR")

    @application.get("/health", include_in_schema=False)
    @application.get("/api/v1/health", tags=["system"])
    async def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @application.get("/ready", response_model=HealthResponse, include_in_schema=False)
    @application.get("/api/v1/ready", response_model=HealthResponse, tags=["system"])
    async def ready() -> JSONResponse:
        try:
            async with get_session_factory()() as database:
                _ = await database.execute(text("select 1"))
        except Exception:  # noqa: BLE001 -- readiness deliberately collapses infrastructure errors
            return JSONResponse(status_code=503, content={"status": "unavailable"})
        return JSONResponse(status_code=200, content={"status": "ok"})

    application.include_router(auth_router, prefix="/api/v1")
    application.include_router(admin_router, prefix="/api/v1")

    assets_root = static_dir or settings.static_dir
    index = assets_root / "index.html"
    assets = assets_root / "assets"
    if index.is_file():
        if assets.is_dir():
            application.mount("/assets", StaticFiles(directory=assets), name="assets")

        @application.get("/{client_path:path}", include_in_schema=False)
        async def spa_fallback(client_path: str) -> FileResponse:
            if client_path == "api" or client_path.startswith("api/") or Path(client_path).suffix:
                raise HTTPException(status_code=404, detail="NOT_FOUND")
            return FileResponse(index, headers={"Cache-Control": "no-cache"})

    return application


app = create_app()
