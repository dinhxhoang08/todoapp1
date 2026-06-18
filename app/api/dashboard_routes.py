from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.services.task_service import TaskService

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def root():
    return RedirectResponse(url="/dashboard", status_code=303)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = TaskService(db)
    stats = svc.get_dashboard_stats(user.id)
    return templates.TemplateResponse(
        "dashboard/index.html",
        {"request": request, "user": user, "stats": stats},
    )


@router.get("/dashboard/stats")
async def dashboard_stats(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = TaskService(db)
    stats = svc.get_dashboard_stats(user.id)
    return JSONResponse(
        content={
            "total_tasks": stats.total_tasks,
            "completed_tasks": stats.completed_tasks,
            "pending_tasks": stats.pending_tasks,
            "in_progress_tasks": stats.in_progress_tasks,
            "archived_tasks": stats.archived_tasks,
            "overdue_tasks": stats.overdue_tasks,
            "completion_rate": stats.completion_rate,
            "tasks_by_status": stats.tasks_by_status,
            "tasks_by_priority": stats.tasks_by_priority,
            "tasks_by_category": stats.tasks_by_category,
        }
    )
