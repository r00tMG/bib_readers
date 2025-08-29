from datetime import datetime

from fastapi import APIRouter, Form, HTTPException, Depends, Request, status
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from src import models, schemas
from src.database import get_db

routes = APIRouter()
templates = Jinja2Templates(directory="templates")

@routes.get("/profile")
async def profile(request:Request, db:Session=Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == request.session.get("user_id")).first()
    #users = [schemas.UserResponse.from_orm(u) for u in user_models]
    #print(user)
    success_emprunt = request.session.pop("success_emprunt", None)
    error_emprunt = request.session.pop("error_emprunt", None)
    return templates.TemplateResponse("/adherents/profile.html",{
        "request":request,
        "user":user,
        "success_emprunt":success_emprunt,
        "error_emprunt":error_emprunt
    })

@routes.post("/api/emprunts")
async def emprunt(
        request: Request,
        id_livre: int = Form(...),
        date_emprunt: str = Form(...),
        date_retour_prevue: str = Form(...),
        date_retour_effectif: str = Form(...),
        db: Session = Depends(get_db)
):
    errors = []
    if not date_emprunt:
        errors.append({"date_emprunt": "Date Emprunt est requis"})
    if not date_retour_prevue:
        errors.append({"date_retour_prevue": "Date Retour Prévue est requis"})
    if not id_livre:
        errors.append({"id_livre": "Id du livre est requis"})
    if date_emprunt > date_retour_prevue:
        errors.append({"error_date":"Le date d'emprunt ne peux pas être supérieur à la date de retour prévue"})
    if errors:
        user = db.query(models.User).filter(models.User.id == request.session.get('user_id')).first()
        return templates.TemplateResponse("/adherents/profile.html", {
            "request": request,
            "errors": errors,
            "user":user
        })
    # Verification de la reservation de ce livre par cet adherent
    test_livre = db.query(models.Reservation).filter(
        (models.Reservation.id_adherent == request.session.get("user_id")), (
                models.Reservation.id_livre == id_livre), (models.Reservation.status == "emprunter")).first()
    if not test_livre:
        new_emprunt = models.Emprunt(
            id_livre=id_livre,
            id_adherent=request.session.get('user_id'),
            date_emprunt=date_emprunt,
            date_retour_prevue=date_retour_prevue
        )
        if not new_emprunt:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Veuillez verifier les données soumis")
        db.add(new_emprunt)
        db.commit()
        db.refresh(new_emprunt)
        query = db.query(models.Reservation).filter(
            models.Reservation.id_adherent == request.session.get("user_id"),
            models.Reservation.id_livre == id_livre
        ).update({
            "status":"emprunter"
        }, synchronize_session=False)
        if query:
            db.commit()
        stock = db.query(models.Livre).filter(models.Livre.id == id_livre).first().stock
        livre_reserved = db.query(models.Livre).filter(models.Livre.id == id_livre).update({
            'stock': stock - 1
        })
        if not livre_reserved:
            raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED,
                                detail=f"Erreur lors de l'update du stock du livre avec l'id: {id_livre}")
        db.commit()
        request.session['success_emprunt'] = {
            "status": "success",
            "message": f"Votre emprunt est validé avec succés: {db.query(models.Livre).filter(models.Livre.id == id_livre).first().titre}"
        }
        return RedirectResponse("/profile", status_code=status.HTTP_303_SEE_OTHER)
    else:
        request.session["error_emprunt"] = {
            "status":"error",
            "message":f"Vous avez un emprunt en cours de ce livre en cours: {db.query(models.Livre).filter(models.Livre.id == id_livre).first().titre}"
        }
        return RedirectResponse("/profile", status_code=status.HTTP_303_SEE_OTHER)



@routes.get("/api/mes-emprunts")
async def mesEmprunts(request:Request, db:Session=Depends(get_db)):
    emprunts = db.query(models.Emprunt).filter(models.Emprunt.id_adherent == request.session.get("user_id"))
    success_retour = request.session.pop("success_retour", None)
    emprunt_exist = request.session.pop("emprunt_exist", None)
    return templates.TemplateResponse("/adherents/emprunts.html",{
        "request":request,
        "emprunts":emprunts,
        "success_retour":success_retour,
        "emprunt_exist":emprunt_exist,
        "today": datetime.utcnow().date()
    })

@routes.post("/api/retours")
async def retour(request:Request, date_retour_effectif:str=Form(...), id_livre:int=Form(...), db:Session=Depends(get_db)):
    errors = []
    if not date_retour_effectif:
        errors.append({"date_retour_effectif":"Date Retour Effectif est requis"})

    test_emprunt = db.query(models.Emprunt).filter(
        models.Emprunt.id_livre == id_livre,
        models.Emprunt.id_adherent == request.session.get("user_id"),
        models.Emprunt.date_retour_effectif != None
    ).first()
    print(test_emprunt)
    if test_emprunt:
        request.session["emprunt_exist"] = {
            "status":"success",
            "message":"Ce livre a déjà été rendu"
        }
        return RedirectResponse("/api/mes-emprunts", status_code=status.HTTP_303_SEE_OTHER)
    db.query(models.Emprunt).filter(models.Emprunt.id_livre == id_livre, models.Emprunt.id_adherent == request.session.get('user_id')).update({
        "date_retour_effectif":date_retour_effectif
    },synchronize_session=False)
    db.commit()
    db.query(models.Reservation).filter(models.Reservation.id_livre == id_livre, models.Reservation.id_adherent == request.session.get('user_id')).update({
        "status":"retourner"
    }, synchronize_session=False)
    db.commit()
    stock = db.query(models.Livre).filter(models.Livre.id == id_livre).first().stock
    print(stock)
    db.query(models.Livre).filter(models.Livre.id == id_livre).update({
        "stock":stock + 1
    })
    db.commit()
    request.session['success_retour'] = {
        "status":"success",
        "message":f"Ce livre a été retourné avec succés ce {date_retour_effectif}"
    }
    return RedirectResponse("/api/mes-emprunts", status_code=status.HTTP_303_SEE_OTHER)
