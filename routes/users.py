from typing import List

from fastapi import APIRouter, Request, Form, Depends, status
from pydantic import EmailStr
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from urllib3 import request

from src import models, schemas
from src.database import get_db
from src.models import UserRole, UserStatus
from src.security import hash_password, login_required, role_admin_required

routes = APIRouter()
#Chargement des fichiers templates
templates = Jinja2Templates(directory="templates")

#Formulaire de l'inscription des utilisateurs
@routes.get("/register", response_class=HTMLResponse)
async def inscription(request: Request):
    error_password = request.session.pop("error_password", None)
    success_register = request.session.pop("success_register", None)
    error_register = request.session.pop("error_register", None)
    return templates.TemplateResponse("/users/inscription.html", {"request":request, "error_password":error_password, "success_register": success_register, "error_register":error_register})

#api pour l'inscription des utilisateurs
@routes.post("/api/register")
async def inscription(request: Request,
                    db:Session = Depends(get_db)
                      ):
    form_data = await request.form()
    fullname = form_data["firstname"] + " " + form_data["lastname"]
    email = form_data["email"]
    password = form_data["password"]
    confirm_password = form_data["confirm_password"]
    errors = []
    if not form_data['firstname']:
        errors.append("Le prénom est obligatoire")
    if not form_data['lastname']:
        errors.append("Le nom est obligatoire")
    if not email:
        errors.append("L'email est obligatoire")
    if not password:
        errors.append("Le mot de passe est obligatoire")
    if password != confirm_password:
        errors.append("Les mots de passe ne correspondent pas")
    if form_data['password'] != form_data["confirm_password"]:
        request.session["error_password"] = {
            "status":"error",
            "message":"Veuillez confirmer votre mot de passe"
        }
        return RedirectResponse("/register", status_code=status.HTTP_303_SEE_OTHER)
    if errors:
        return templates.TemplateResponse("/users/inscription.html", {"request":request, "errors":errors})
    new_user = models.User(
        fullname = fullname,
        email = email,
        password = hash_password(password)
    )
    if new_user:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        request.session['success_register'] = {
            "status":"success",
            "message":"Votre inscription a réussi avec succés"
        }
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    request.session['error_register'] = {
        "status":"error",
        "message":"Veuillez verifier les données entrées"
    }
    return RedirectResponse(url="/register", status_code=status.HTTP_303_SEE_OTHER)



