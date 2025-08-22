from fastapi import Request, Form, Depends, status
from fastapi.routing import APIRouter
from pydantic import EmailStr
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from urllib3 import request

from src import models, schemas
from src.database import get_db
from src.security import verify_password, login_required

routes = APIRouter()

templates = Jinja2Templates(directory="templates")


@routes.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    error_login = request.session.pop("error_login", None)
    success_logout = request.session.pop("success_logout", None)
    success_register = request.session.pop("success_register", None)
    return templates.TemplateResponse("/auth/login.html", {"request": request, "error_login":error_login, "success_logout":success_logout})


@routes.post("/api/login", response_class=HTMLResponse, response_model=schemas.UserResponse)
async def login(request: Request,
                db: Session = Depends(get_db)):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    user = db.query(models.User).filter(models.User.email == email).first()
    user_response = schemas.UserResponse.from_orm(user)
    errors = []
    if not email or not password:
        errors.append({"email":"Mauvais identifiants"})
        print(errors)
        return templates.TemplateResponse("auth/login.html", {'request': request,"errors":errors } )

    if email != user_response.email or not verify_password(password, user.password):
        request.session['error_login'] = {
           "status":"error",
            "message":"Mauvaise identifiants"
        }
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    request.session['user_id'] = user_response.id
    print("role de l'utilisateur: ", user_response.role)

    request.session['role'] = user_response.role
    request.session["success_login"] = {
        "status":"success",
        "message":"Connexion réussie, Bienvenu dans BIBREADERS"
    }
    return RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)


@routes.get("/logout")
@login_required
async def logout(request:Request):
    if request.session.get("user_id"):
        print(request.session.get("user_id"))
        del request.session["user_id"]
        request.session["success_logout"] = {
            "status":"success",
            "message":"Déconnexion réussie"
        }
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)