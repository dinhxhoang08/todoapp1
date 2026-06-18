from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.core.dependencies import get_db, get_current_user
from app.services.category_service import CategoryService
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.models.user import User

router = APIRouter(prefix="/categories", tags=["categories"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def list_categories(
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = CategoryService(db)
    categories = svc.list_categories(user.id)
    return templates.TemplateResponse(
        "categories/list.html",
        {"request": request, "user": user, "categories": categories},
    )


@router.get("/new", response_class=HTMLResponse)
async def new_category_form(request: Request):
    return templates.TemplateResponse(
        "categories/form.html",
        {"request": request, "category": None},
    )


@router.post("", response_class=HTMLResponse)
async def create_category(
    request: Request,
    name: str = Form(...),
    color: Optional[str] = Form(None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = CategoryService(db)
    svc.create_category(user.id, CategoryCreate(name=name, color=color))
    categories = svc.list_categories(user.id)
    return templates.TemplateResponse(
        "categories/list.html",
        {"request": request, "user": user, "categories": categories},
    )


@router.get("/{id}/edit", response_class=HTMLResponse)
async def edit_category_form(
    request: Request,
    id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = CategoryService(db)
    category = svc.category_repo.get_by_user(user.id, id)
    return templates.TemplateResponse(
        "categories/form.html",
        {"request": request, "category": category},
    )


@router.put("/{id}", response_class=HTMLResponse)
async def update_category(
    request: Request,
    id: int,
    name: str = Form(...),
    color: Optional[str] = Form(None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = CategoryService(db)
    svc.update_category(user.id, id, CategoryUpdate(name=name, color=color))
    categories = svc.list_categories(user.id)
    return templates.TemplateResponse(
        "categories/list.html",
        {"request": request, "user": user, "categories": categories},
    )


@router.delete("/{id}")
async def delete_category(
    id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = CategoryService(db)
    svc.delete_category(user.id, id)
    return JSONResponse({"success": True})
