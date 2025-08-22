import os
import shutil
from typing import List, Optional

from fastapi import APIRouter, Request, UploadFile, Depends, Form, File, Query
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.templating import Jinja2Templates

from src import models, schemas
from src.database import get_db
from src.security import role_admin_required

routes = APIRouter()

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@routes.get("/admin/gestion-livres", response_model=List[schemas.LivreResponse])
@role_admin_required
async def gestion_livre(request: Request,search:Optional[str]=Query(None, Nonedescription="Mot-clé de la recherche"), db: Session = Depends(get_db)):
    print(search)
    if search:
        query = db.query(models.Livre).filter(models.Livre.titre.ilike(f"%{search}%"))
    else:
        query = db.query(models.Livre)
    livres = query.all()
    livre_responses = [schemas.LivreResponse.from_orm(l).dict() for l in livres]
    success_deleted = request.session.pop("success_deleted", None)
    success_updated = request.session.pop("success_updated", None)
    success_create_livre = request.session.pop("success_create_livre", None)
    return templates.TemplateResponse("/admin/gestion-livres.html", {"request": request,
                                                                     "livres": livre_responses,
                                                                     "success_deleted": success_deleted,
                                                                     "success_updated": success_updated,
                                                                     "success_create_livre":success_create_livre,
                                                                     "search":search
                                                                     })


@routes.get("/admin/create/livre", response_class=HTMLResponse)
@role_admin_required
async def create_livre(request: Request):
    error_save_livre = request.session.pop("error_save_livre", None)
    success_updated = request.session.pop("success_updated", None)
    errors = request.session.pop("errors", None)
    return templates.TemplateResponse("/admin/create_livre.html", {
        "request": request,
        "error_save_livre": error_save_livre,
        "success_updated": success_updated,
        "errors":errors
    })


@routes.post("/api/create_livre")
@role_admin_required
async def add_livre(request: Request,
                    titre: str = Form(...),
                    description: str = Form(...),
                    image_url: UploadFile = File(...),
                    stock: int = Form(...),
                    rating: int = Form(...),
                    db: Session = Depends(get_db)
                    ):
    print(await request.form())
    errors = []
    if not image_url.filename:
        errors.append({
            "image_url": "L'image est requis"
        })
    if errors:
        request.session['errors'] = errors
        return RedirectResponse(url=f"/admin/create/livre",
                                status_code=status.HTTP_303_SEE_OTHER)
    file_path = os.path.join(UPLOAD_DIR, image_url.filename)

    # Sauvegarde de l'image
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image_url.file, buffer)
    print(file_path)
    new_livre = models.Livre(
        titre=titre,
        description=description,
        image_url=file_path,
        stock=stock,
        rating=rating
    )
    if new_livre:
        db.add(new_livre)
        db.commit()
        db.refresh(new_livre)
        request.session['success_create_livre'] = {
            "status": "success",
            "message": "Livre créé avec succés"
        }
        return RedirectResponse(url="/admin/gestion-livres", status_code=status.HTTP_303_SEE_OTHER)
    else:
        request.session['error_save_livre'] = {
            "status": "success",
            "message": "Verifier vos données"
        }
        return RedirectResponse("/admin/create/livre", status_code=status.HTTP_303_SEE_OTHER)


@routes.get("/update_livre/{id}", response_model=schemas.LivreResponse)
@role_admin_required
async def update(request: Request, id: int, db: Session = Depends(get_db)):
    request.session['id_livre_to_update'] = id
    livre = db.query(models.Livre).filter(models.Livre.id == id).first()
    livre_updated = schemas.LivreResponse.from_orm(livre)
    error_updated = request.session.pop("error_updated", None)
    error_id_undefined = request.session.pop("error_id_undefined", None)
    errors = request.session.get("errors")
    return templates.TemplateResponse("/admin/update_livre.html", {
        "request": request,
        "livre": livre_updated,
        "error_updated": error_updated,
        "error_id_undefined": error_id_undefined,
        "errors":errors
    })


@routes.post("/api/update_livre", response_class=HTMLResponse)
@role_admin_required
async def update(
        request: Request,
        titre: str = Form(...),
        description: str = Form(...),
        image_url: UploadFile = File(...),
        stock: int = Form(...),
        rating: int = Form(...),
        db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOAD_DIR, image_url.filename)
    print(not image_url.filename)
    errors = []
    if not image_url.filename:
        errors.append({
            "image_url" : "L'image est requis"
        })
    if errors:
        request.session['errors'] = errors
        return RedirectResponse(url=f"/update_livre/{request.session.get('id_livre_to_update')}",
                                    status_code=status.HTTP_303_SEE_OTHER)
    with open(file_path, "wb") as file:
        shutil.copyfileobj(image_url.file, file)
    if request.session.get('id_livre_to_update'):
        query = db.query(models.Livre).filter(models.Livre.id == request.session.get("id_livre_to_update")).update({
            'titre': titre,
            'description': description,
            'image_url': file_path,
            'stock': stock,
            'rating': rating
        }, synchronize_session=False)
        if query:
            db.commit()
            request.session['success_updated'] = {
                "success": "success",
                "message": "La modification est faite avec succés"
            }
            return RedirectResponse(url="/admin/gestion-livres", status_code=status.HTTP_303_SEE_OTHER)
        else:
            request.session['error_updated'] = {
                "error": "error",
                "message": "Erreur lors de la mis à jour"
            }
            return RedirectResponse(url=f"/update_livre/{request.session.get('id_livre_to_update')}",
                                    status_code=status.HTTP_303_SEE_OTHER)
    else:
        request.session["error_id_undefined"] = {
            "error": "error",
            "message": "Ce livre avec cet id n'a pas été trouvé"
        }
        return RedirectResponse(url=f"/update_livre/{request.session.get('id_livre_to_update')}",
                                status_code=status.HTTP_303_SEE_OTHER)


@routes.post("/delete/livre/{id}")
@role_admin_required
async def delete(request: Request, id: int, db: Session = Depends(get_db)):
    query = db.query(models.Livre).filter(models.Livre.id == id).delete(synchronize_session=False)
    if query:
        db.commit()
        print("Reste to commit")
        request.session['success_deleted'] = {
            "status": "success",
            "message": "Supprimer avec succés"
        }
        return RedirectResponse(url="/admin/gestion-livres", status_code=status.HTTP_303_SEE_OTHER)


@routes.get("/api/livres/{id}")
@role_admin_required
async def show(request:Request, id:int, db:Session=Depends(get_db)):
    if id:
        livre = db.query(models.Livre).filter(models.Livre.id == id).first()
        livre_response = schemas.LivreResponse.from_orm(livre)
        return templates.TemplateResponse("/admin/livre.html", {
            "request":request,
            "livre":livre_response
        })
    else:
        request.session['error_id_undefine'] = {
            "status":"error",
            "message":f"Livre avec ce id n'existe pas: {id}"
        }
        return RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)

@routes.post("/api/reservations")
async def reservation(request:Request,id_livre:int=Form(), db:Session=Depends(get_db)):
    print(id_livre)
    livre = db.query(models.Livre).filter(models.Livre.id == id_livre).first()
    
    if livre.stock != 0:
        #Creation de la reservation
        new_reservation = models.Reservation(
            id_livre = id_livre,
            id_adherent = request.session.get('user_id')
        )
        db.add(new_reservation)
        db.commit()
        db.refresh(new_reservation)
        #Update disponibility
        this_livre = db.query(models.Livre).filter(models.Livre.id == id_livre).first()

    return templates.TemplateResponse("home.html", {
        "request":request
    })