from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.schemas.user import UserCreate, UserLogin, ChangePasswordRequest, UserUpdate
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember_me: bool = Form(False),
    db: Session = Depends(get_db),
):
    svc = AuthService(db)
    try:
        token = svc.login(UserLogin(username=username, password=password, remember_me=remember_me))
        response = RedirectResponse(url="/dashboard", status_code=303)
        max_age = 60 * 60 * 24 * 7 if remember_me else None
        response.set_cookie(
            "access_token", token, httponly=True, secure=False, samesite="lax", max_age=max_age
        )
        return response
    except Exception as e:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": str(e.detail) if hasattr(e, "detail") else str(e)},
        )


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    svc = AuthService(db)
    try:
        user = svc.register(UserCreate(username=username, email=email, password=password))
        token = svc.login(UserLogin(username=username, password=password))
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie("access_token", token, httponly=True, secure=False, samesite="lax")
        return response
    except Exception as e:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": str(e.detail) if hasattr(e, "detail") else str(e)},
        )


@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        "profile/index.html",
        {"request": request, "user": user},
    )


@router.post("/profile/update")
async def update_profile(
    request: Request,
    username: str = Form(None),
    email: str = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = AuthService(db)
    try:
        svc.user_repo.update(user.id, {k: v for k, v in {"username": username, "email": email}.items() if v})
        return templates.TemplateResponse(
            "profile/index.html",
            {"request": request, "user": user, "success": "Profile updated successfully"},
        )
    except Exception as e:
        return templates.TemplateResponse(
            "profile/index.html",
            {"request": request, "user": user, "error": str(e.detail) if hasattr(e, "detail") else str(e)},
        )


@router.post("/change-password")
async def change_password(
    request: Request,
    old_password: str = Form(...),
    new_password: str = Form(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = AuthService(db)
    try:
        svc.change_password(user.id, old_password, new_password)
        return templates.TemplateResponse(
            "profile/index.html",
            {"request": request, "user": user, "success": "Password changed successfully"},
        )
    except Exception as e:
        return templates.TemplateResponse(
            "profile/index.html",
            {"request": request, "user": user, "error": str(e.detail) if hasattr(e, "detail") else str(e)},
        )
