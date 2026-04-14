"""
FastAPI application entry point for the AutoAssur pricing API.
Start with: uvicorn auto_insurance.api.main:app --reload
"""

import logging
import os
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse

from auto_insurance.api.endpoints.health import router as health_router
from auto_insurance.api.endpoints.predict import router as predict_router
from auto_insurance.api.logging_config import setup_logging

# ── Logging setup ───────────────────────────────────────────────────────────
# Must be called BEFORE any logger is created in imported modules.
# Log level can be overridden via the LOG_LEVEL environment variable.
setup_logging(level=os.getenv("LOG_LEVEL", "INFO"))

logger = logging.getLogger(__name__)

# ── FastAPI application ─────────────────────────────────────────────────────
app = FastAPI(
    title="AutoAssur — Motor Insurance Pricing API",
    description=(
        "REST API powered by two XGBoost models to compute the pure premium in real time.\n\n"
        "**Actuarial formula**: Pure Premium = Frequency × Severity\n\n"
        "- `/predict/frequency` — claim probability\n"
        "- `/predict/severity` — average claim cost\n"
        "- `/predict/premium` — full pure premium\n"
        "- `/predict/explain` — pure premium + risk factors (SHAP)"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(health_router)
app.include_router(predict_router)


# ── Request logging middleware ──────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    """
    HTTP middleware that logs every incoming request with:
    - a short unique request ID
    - HTTP method and path
    - response status code
    - end-to-end latency in milliseconds

    This middleware runs for ALL requests, including /health.
    It complements — but does not replace — the business-level
    logs written inside each endpoint handler.
    """
    request_id = str(uuid.uuid4())[:8]
    start_time = time.perf_counter()

    logger.info(
        "Request received",
        extra={
            "endpoint": str(request.url.path),
            "method": request.method,
            "request_id": request_id,
        },
    )

    response = await call_next(request)

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    logger.info(
        "Request completed",
        extra={
            "endpoint": str(request.url.path),
            "method": request.method,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "request_id": request_id,
        },
    )

    return response


# ── Landing page ────────────────────────────────────────────────────────────
_DASHBOARD = Path(__file__).parent / "dashboard.html"


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def landing_page() -> HTMLResponse:
    """Serve the interactive pricing dashboard."""
    return HTMLResponse(content=_DASHBOARD.read_text(encoding="utf-8"))
