"""Application entry point for the auto insurance FastAPI service."""

import logging
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.responses import Response

from auto_insurance.api.endpoints.health import router as health_router
from auto_insurance.api.endpoints.predict import router as predict_router
from auto_insurance.api.logging_utils import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AutoAssur API",
    description="API REST pour predire la frequence, la gravite et la prime pure.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(health_router)
app.include_router(predict_router)


@app.middleware("http")
async def add_request_context(request: Request, call_next) -> Response:
    """Attach a request id and log the request lifecycle."""
    request_id = request.headers.get("x-request-id", str(uuid4()))
    logger.info(
        "Request started id=%s method=%s path=%s",
        request_id,
        request.method,
        request.url.path,
    )
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "Request completed id=%s method=%s path=%s status=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
    )
    return response


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def landing_page() -> str:
    """Return a minimal HTML landing page."""
    return """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AutoAssur API</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; padding: 2rem; background: #f7fafc; color: #1a202c; }
    .card { max-width: 760px; margin: 0 auto; background: white; padding: 2rem; border-radius: 16px; box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08); }
    h1 { margin-top: 0; color: #1d4ed8; }
    ul { line-height: 1.8; }
    a { color: #2563eb; text-decoration: none; }
    code { background: #eff6ff; padding: 0.15rem 0.35rem; border-radius: 6px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>AutoAssur API</h1>
    <p>API de tarification automobile avec endpoints de prediction, logs de requetes et audit SQLite optionnel.</p>
    <ul>
      <li><code>GET /health</code></li>
      <li><code>GET /health/models</code></li>
      <li><code>GET /health/audit</code></li>
      <li><code>POST /predict/frequency</code></li>
      <li><code>POST /predict/severity</code></li>
      <li><code>POST /predict/premium</code></li>
      <li><code>POST /predict/explain</code></li>
    </ul>
    <p>
      Documentation:
      <a href="/docs">Swagger UI</a>
      |
      <a href="/redoc">ReDoc</a>
    </p>
  </div>
</body>
</html>
"""
