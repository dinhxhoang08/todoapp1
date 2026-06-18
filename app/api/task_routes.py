from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.dependencies import get_db, get_current_user
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.models.user import User

router = APIRouter(prefix="/tasks", tags=["tasks"])
templates = Jinja2Templates(directory="app/templates")
api_router = APIRouter(prefix="/api/tasks", tags=["tasks-api"])


# ---- HTML Routes (HTMX-enhanced) ----

@router.get("", response_class=HTMLResponse)
async def list_tasks(
    request: Request,
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    search_query: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    skip: int = Query(0),
    limit: int = Query(50),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = TaskService(db)
    tasks = svc.list_tasks(
        user.id,
        status=status,
        priority=priority,
        category_id=category_id,
        search_query=search_query,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
    )
    return templates.TemplateResponse(
        "tasks/list.html",
        {"request": request, "user": user, "tasks": tasks},
    )


@router.get("/task_rows", response_class=HTMLResponse)
async def task_rows(
    request: Request,
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    search_query: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    skip: int = Query(0),
    limit: int = Query(50),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = TaskService(db)
    tasks = svc.list_tasks(
        user.id,
        status=status,
        priority=priority,
        category_id=category_id,
        search_query=search_query,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
    )
    return templates.TemplateResponse(
        "tasks/task_rows.html",
        {"request": request, "tasks": tasks},
    )


@router.get("/new", response_class=HTMLResponse)
async def new_task_form(
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.services.category_service import CategoryService
    from app.services.tag_service import TagService
    cs = CategoryService(db)
    ts = TagService(db)
    categories = cs.list_categories(user.id)
    tags = ts.list_tags(user.id)
    return templates.TemplateResponse(
        "tasks/form.html",
        {"request": request, "categories": categories, "tags": tags, "task": None},
    )


@router.post("", response_class=HTMLResponse)
async def create_task(
    request: Request,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    priority: str = Form("medium"),
    due_date: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    tag_ids: Optional[str] = Form(None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from datetime import datetime
    from dateutil import parser
    svc = TaskService(db)
    parsed_due = parser.parse(due_date) if due_date else None
    parsed_tag_ids = [int(t) for t in tag_ids.split(",") if t.strip()] if tag_ids else None
    task = svc.create_task(
        user.id,
        TaskCreate(
            title=title,
            description=description,
            priority=priority,
            due_date=parsed_due,
            category_id=category_id,
            tag_ids=parsed_tag_ids,
        ),
    )
    tasks = svc.list_tasks(user.id, limit=50)
    return templates.TemplateResponse(
        "tasks/task_rows.html",
        {"request": request, "tasks": tasks},
    )


@router.get("/{id}/edit", response_class=HTMLResponse)
async def edit_task_form(
    request: Request,
    id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.services.category_service import CategoryService
    from app.services.tag_service import TagService
    svc = TaskService(db)
    cs = CategoryService(db)
    ts = TagService(db)
    task = svc.get_task(user.id, id)
    categories = cs.list_categories(user.id)
    tags = ts.list_tags(user.id)
    return templates.TemplateResponse(
        "tasks/form.html",
        {"request": request, "task": task, "categories": categories, "tags": tags},
    )


@router.put("/{id}", response_class=HTMLResponse)
async def update_task(
    request: Request,
    id: int,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    priority: str = Form("medium"),
    status: str = Form("pending"),
    due_date: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    tag_ids: Optional[str] = Form(None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from dateutil import parser
    svc = TaskService(db)
    parsed_due = parser.parse(due_date) if due_date else None
    parsed_tag_ids = [int(t) for t in tag_ids.split(",") if t.strip()] if tag_ids else None
    svc.update_task(
        user.id,
        id,
        TaskUpdate(
            title=title,
            description=description,
            priority=priority,
            status=status,
            due_date=parsed_due,
            category_id=category_id,
            tag_ids=parsed_tag_ids,
        ),
    )
    tasks = svc.list_tasks(user.id, limit=50)
    return templates.TemplateResponse(
        "tasks/task_rows.html",
        {"request": request, "tasks": tasks},
    )


@router.delete("/{id}")
async def delete_task(
    id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = TaskService(db)
    svc.delete_task(user.id, id)
    return JSONResponse({"success": True}, status_code=200)


@router.post("/{id}/complete")
async def complete_task(
    id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = TaskService(db)
    svc.complete_task(user.id, id)
    return JSONResponse({"success": True})


@router.post("/{id}/archive")
async def archive_task(
    id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = TaskService(db)
    svc.archive_task(user.id, id)
    return JSONResponse({"success": True})


@router.post("/{id}/restore")
async def restore_task(
    id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = TaskService(db)
    svc.restore_task(user.id, id)
    return JSONResponse({"success": True})


@router.post("/{id}/duplicate")
async def duplicate_task(
    id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = TaskService(db)
    svc.duplicate_task(user.id, id)
    return JSONResponse({"success": True})


# ---- JSON REST API Routes ----

@api_router.get("")
async def api_list_tasks(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    search_query: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    skip: int = Query(0),
    limit: int = Query(50),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = TaskService(db)
    tasks = svc.list_tasks(
        user.id,
        status=status,
        priority=priority,
        category_id=category_id,
        search_query=search_query,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
    )
    return [
        TaskResponse(
            id=t.id,
            user_id=t.user_id,
            category_id=t.category_id,
            title=t.title,
            description=t.description,
            status=t.status,
            priority=t.priority,
            due_date=t.due_date,
            completed_at=t.completed_at,
            created_at=t.created_at,
            updated_at=t.updated_at,
            category_name=t.category.name if t.category else None,
            tag_names=[tag.name for tag in t.tags] if t.tags else None,
        )
        for t in tasks
    ]


@api_router.get("/{id}")
async def api_get_task(
    id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = TaskService(db)
    t = svc.get_task(user.id, id)
    return TaskResponse(
        id=t.id,
        user_id=t.user_id,
        category_id=t.category_id,
        title=t.title,
        description=t.description,
        status=t.status,
        priority=t.priority,
        due_date=t.due_date,
        completed_at=t.completed_at,
        created_at=t.created_at,
        updated_at=t.updated_at,
        category_name=t.category.name if t.category else None,
        tag_names=[tag.name for tag in t.tags] if t.tags else None,
    )


@api_router.post("", status_code=201)
async def api_create_task(
    task_data: TaskCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = TaskService(db)
    t = svc.create_task(user.id, task_data)
    return TaskResponse(
        id=t.id,
        user_id=t.user_id,
        category_id=t.category_id,
        title=t.title,
        description=t.description,
        status=t.status,
        priority=t.priority,
        due_date=t.due_date,
        completed_at=t.completed_at,
        created_at=t.created_at,
        updated_at=t.updated_at,
        category_name=t.category.name if t.category else None,
        tag_names=[tag.name for tag in t.tags] if t.tags else None,
    )


@api_router.put("/{id}")
async def api_update_task(
    id: int,
    task_data: TaskUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = TaskService(db)
    t = svc.update_task(user.id, id, task_data)
    return TaskResponse(
        id=t.id,
        user_id=t.user_id,
        category_id=t.category_id,
        title=t.title,
        description=t.description,
        status=t.status,
        priority=t.priority,
        due_date=t.due_date,
        completed_at=t.completed_at,
        created_at=t.created_at,
        updated_at=t.updated_at,
        category_name=t.category.name if t.category else None,
        tag_names=[tag.name for tag in t.tags] if t.tags else None,
    )


@api_router.delete("/{id}", status_code=204)
async def api_delete_task(
    id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = TaskService(db)
    svc.delete_task(user.id, id)
