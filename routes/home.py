from typing import Optional

from fastapi.params import Depends, Query
from fastapi.routing import APIRouter, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from src import models
from src.database import get_db
from src.security import login_required

routes = APIRouter()

templates = Jinja2Templates(directory="templates")

@routes.get("/home", response_class=HTMLResponse)
@login_required
async def home(
        request:Request,
        search:Optional[str]=Query(None),
        page: int = Query(1, ge=1),
        per_page: int = 8,
        db:Session=Depends(get_db)
    ):
    if search:
        query = db.query(models.Livre).filter(models.Livre.titre.ilike(f"%{search}%"))
    else:
        query = db.query(models.Livre)
    total = query.count()
    livres = query.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = (total + per_page - 1) // per_page


    success_login = request.session.pop("success_login", None)
    unauthorize = request.session.pop("unauthorize", None)
    error_id_undefine = request.session.pop("error_id_undefine", None)
    success_reservation = request.session.pop("success_reservation",None)
    reservation_indisponible = request.session.pop("reservation_indisponible", None)
    livre_deja_reserved_par_vous = request.session.pop("livre_deja_reserved_par_vous", None)
    return templates.TemplateResponse("/home.html", {
        "request":request,
        "success_login":success_login,
        "unauthorize":unauthorize,
        "error_id_undefine":error_id_undefine,
        "success_reservation":success_reservation,
        "page":page,
        "livres":livres,
        "search":search,
        "reservation_indisponible":reservation_indisponible,
        "livre_deja_reserved_par_vous":livre_deja_reserved_par_vous,
        "total_pages": total_pages
    })