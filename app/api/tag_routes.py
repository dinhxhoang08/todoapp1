from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.core.dependencies import get_db, get_current_user
from app.services.tag_service import TagService
from app.schemas.tag import TagCreate
from app.models.user import User

router = APIRouter(prefix="/tags", tags=["tags"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def list_tags(
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = TagService(db)
    tags = svc.list_tags(user.id)
    return templates.TemplateResponse(
        "tags/list.html",
        {"request": request, "user": user, "tags": tags},
    )


@router.get("/new", response_class=HTMLResponse)
async def new_tag_form(request: Request):
    return templates.TemplateResponse(
        "tags/form.html",
        {"request": request},
    )


@router.post("", response_class=HTMLResponse)
async def create_tag(
    request: Request,
    name: str = Form(...),
    color: Optional[str] = Form(None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = TagService(db)
    svc.create_tag(user.id, TagCreate(name=name, color=color))
    tags = svc.list_tags(user.id)
    return templates.TemplateResponse(
        "tags/list.html",
        {"request": request, "user": user, "tags": tags},
    )


@router.delete("/{id}")
async def delete_tag(
    id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = TagService(db)
    svc.delete_tag(user.id, id)
    return JSONResponse({"success": True})
