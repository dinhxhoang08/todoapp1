from fastapi import APIRouter
from app.api.auth_routes import router as auth_router
from app.api.dashboard_routes import router as dashboard_router
from app.api.task_routes import router as task_router
from app.api.category_routes import router as category_router
from app.api.tag_routes import router as tag_router
from app.api.export_routes import router as export_router

html_router = APIRouter()
html_router.include_router(auth_router)
html_router.include_router(dashboard_router)
html_router.include_router(task_router)
html_router.include_router(category_router)
html_router.include_router(tag_router)
html_router.include_router(export_router)
