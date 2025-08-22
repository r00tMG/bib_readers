from fastapi.routing import APIRouter, Request
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from src.security import login_required

routes = APIRouter()

templates = Jinja2Templates(directory="templates")

@routes.get("/home", response_class=HTMLResponse)
@login_required
async def home(request:Request):
    success_login = request.session.pop("success_login", None)
    unauthorize = request.session.pop("unauthorize", None)
    error_id_undefine = request.session.pop("error_id_undefine", None)
    return templates.TemplateResponse("/home.html", {
        "request":request,
        "success_login":success_login,
        "unauthorize":unauthorize,
        "error_id_undefine":error_id_undefine
    })