import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Ensure the project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone
from app.core.config import settings
from app.database.session import init_db
from app.api.router import html_router
from app.api.task_routes import api_router as task_api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Todo App",
    description="A production-ready Todo List web application",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include HTML routers
app.include_router(html_router)

# Include JSON API routers
app.include_router(task_api_router)

templates = Jinja2Templates(directory="app/templates")

# Add now() function to template globals
templates.env.globals["now"] = lambda: datetime.now(timezone.utc)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
        "base.html",
        {"request": request, "error": "Page not found"},
        status_code=404,
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return templates.TemplateResponse(
        "base.html",
        {"request": request, "error": "Internal server error"},
        status_code=500,
    )
