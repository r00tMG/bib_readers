from typing import List

from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from src import schemas, models
from src.database import get_db
from src.models import UserRole, UserStatus
from src.security import role_admin_required, hash_password

routes = APIRouter()
templates = Jinja2Templates(directory="templates")
#Page de la gestion des utilisateurs
@routes.get("/admin/gestion-adherents", response_model=List[schemas.UserResponse])
@role_admin_required
async def gestAdherents(request:Request, db:Session=Depends(get_db)):
    users = db.query(models.User).all()
    users_response = [schemas.UserResponse.from_orm(u).dict() for u in users]
    success_update = request.session.pop('success_update', None)
    success_deleted = request.session.pop('success_deleted', None)
    error_deleted = request.session.pop('error_deleted', None)
    error_update = request.session.pop('error_update', None)
    success_suspend = request.session.pop("success_suspend", None)
    error_suspend = request.session.pop("error_suspend", None)
    return templates.TemplateResponse("admin/gestion-adherents.html", {
        "request": request,
        "users":users_response,
        "success_update":success_update,
        "success_deleted":success_deleted,
        "error_deleted":error_deleted,
        "error_update":error_update,
        "success_suspend" : success_suspend,
        "error_suspend" : error_suspend
    })

#Formulaire pour le modification d'un utilisateur
@routes.get('/modify/{id}', response_model=schemas.UserResponse)
@role_admin_required
async def modify(request:Request, id : int, db:Session=Depends(get_db)):
    print("id = ", id)
    request.session['user_id_updated']=id
    user = db.query(models.User).filter(models.User.id == id).first()
    user_response = schemas.UserResponse.from_orm(user)
    error_password = request.session.pop('error_password', None)
    return templates.TemplateResponse("/admin/modify.html", {
        "request":request,
        "user":user_response,
        "error_password":error_password,
    })

#Serive de la modification d'un utilisateur
@routes.post('/api/modify', response_model=schemas.UserResponse)
@role_admin_required
async def modify(
        request:Request,
        fullname:str = Form(...),
        email:str=Form(...),
        role:UserRole=Form(...),
        stat:UserStatus=Form(...),
        password:str=Form(...),
        confirm_password:str=Form(...),
        db:Session=Depends(get_db)):
    if password != confirm_password:
        request.session['error_password'] = {
            "status":"error",
            "message":"Password non confirmé"
        }
        return RedirectResponse(url=f"/modify/{request.session.get("user_id_updated")}")
    if not password:
        query = db.query(models.User).filter(models.User.id == request.session.get('user_id_updated')).update({
            "fullname" : fullname,
            "email" : email,
            "role" : role,
            "status" : stat,
        }, synchronize_session=False)
    else:
        query = db.query(models.User).filter(models.User.id == request.session.get('user_id_updated')).update({
            "fullname": fullname,
            "email": email,
            "role": role,
            "status": stat,
            "password": hash_password(password)
        }, synchronize_session=False)

    print("response", query)
    if query:
        db.commit()
        request.session['success_update'] = {
            "status":"success",
            "message":"Adhérent modifié avec succés"
        }
    else:
        request.session['error_update'] = {
            "status": "success",
            "message": "Modification échoué avec succés"
        }

    return RedirectResponse(url="/admin/gestion-adherents", status_code=status.HTTP_303_SEE_OTHER)

#Service pour la suppression d'un utilisateur
@routes.post("/delete/{id}", response_class=HTMLResponse)
@role_admin_required

async def delete(request:Request, id:int, db:Session=Depends(get_db)):
    print("id user to delete: ",id)
    if id:
        db.query(models.User).filter(models.User.id == id).delete(synchronize_session=False)
        db.commit()
        request.session["success_deleted"] = {
            "status":"success",
            "message":"Adhérent supprimé avec succés"
        }
        return RedirectResponse(url="/admin/gestion-adherents", status_code=status.HTTP_303_SEE_OTHER)
    else:
        request.session["error_deleted"] = {
            "status": "success",
            "message": "Suppression échoué"
        }


# Service pour la suspension d'un utilisateur
@routes.post("/suspend/{id}")
@role_admin_required
async def suspend(request:Request, id:int, db:Session=Depends(get_db)):
    print('l\'id de l\'utilisateur est: ', id)
    if id:
        db.query(models.User).filter(models.User.id == id).update({
            "status": UserStatus.SUSPENDRE
        }, synchronize_session=False)
        db.commit()
        request.session['success_suspend'] = {
            "status":"success",
            "message":"La suspension a réussi"
        }
        return RedirectResponse("/admin/gestion-adherents", status_code=status.HTTP_303_SEE_OTHER)
    else:
        request.session['error_suspend'] = {
            "status": "success",
            "message": "La suspension a échoué"
        }
        return RedirectResponse("/admin/gestion-adherents", status_code=status.HTTP_303_SEE_OTHER)
