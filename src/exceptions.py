from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

async def validation_exception_handler_register(request: Request, exc:RequestValidationError):
    return templates.TemplateResponse("/users/inscription.html",{
        "request":request,
        "errors":exc.errors(),
        "form_data":await request.form()
    }, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

async def validation_exception_handler_login(request: Request, exc:RequestValidationError):
    return templates.TemplateResponse("/auth/login.html",{
        "request":request,
        "errors":exc.errors(),
        "form_data":await request.form()
    }, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


async def validation_exception_handler_modify(request: Request, exc:RequestValidationError):
    return templates.TemplateResponse("/admin/modify.html",{
        "request":request,
        "errors":exc.errors(),
        "form_data":await request.form()
    },  status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

async def validation_exception_handler_update_livre(request: Request, exc:RequestValidationError):
    return templates.TemplateResponse("/admin/update_livre.html",{
        "request":request,
        "errors":exc.errors(),
        "form_data":await request.form()
    },  status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)