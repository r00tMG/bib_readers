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
    print(date_emprunt, date_retour_prevue, id_livre)
    errors = []
    if not date_emprunt:
        errors.append({"date_emprunt": "Date Emprunt est requis"})
    if not date_retour_prevue:
        errors.append({"date_retour_prevue": "Date Retour Prévue est requis"})
    if not id_livre:
        errors.append({"id_livre": "Id du livre est requis"})
    if errors:
        return templates.TemplateResponse("/adherents/profile.html", {
            "request": request,
            "errors": errors
        })
    print("test1")
    # Verification de la reservation de ce livre par cet adherent
    test_livre = db.query(models.Reservation).filter(
        (models.Reservation.id_adherent == request.session.get("user_id")), (
                models.Reservation.id_livre == id_livre), (models.Reservation.status == "emprunter")).first()
    print("test2")
    if not test_livre:
        print("test3")
        new_emprunt = models.Emprunt(
            id_livre=id_livre,
            id_adherent=request.session.get('user_id'),
            date_emprunt=date_emprunt,
            date_retour_prevue=date_retour_prevue
        )
        if not new_emprunt:
            print("test4")
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Veuillez verifier les données soumis")
        db.add(new_emprunt)
        db.commit()
        db.refresh(new_emprunt)
        print("test5")
        query = db.query(models.Reservation).filter(
            models.Reservation.id_adherent == request.session.get("user_id"),
            models.Reservation.id_livre == id_livre
        ).update({
            "status":"emprunter"
        }, synchronize_session=False)
        if query:
            db.commit()
        print("test6")
        request.session['success_emprunt'] = {
            "status": "success",
            "message": f"Votre emprunt est validé avec succés: {db.query(models.Livre).filter(models.Livre.id == id_livre).first().titre}"
        }
        return RedirectResponse("/profile", status_code=status.HTTP_303_SEE_OTHER)
    else:
        print("test7")
        request.session["error_emprunt"] = {
            "status":"error",
            "message":f"Vous avez un emprunt en cours de ce livre en cours: {db.query(models.Livre).filter(models.Livre.id == id_livre).first().titre}"
        }
        return RedirectResponse("/profile", status_code=status.HTTP_303_SEE_OTHER)



@routes.get("/api/mes-emprunts")
async def mesEmprunts(request:Request, db:Session=Depends(get_db)):
    emprunts = db.query(models.Emprunt).filter(models.Emprunt.id_adherent == request.session.get("user_id"))
    print(emprunts)
    user = []
    return templates.TemplateResponse("/adherents/emprunts.html",{
        "request":request,
        "emprunts":emprunts,
    })