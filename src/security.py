from fastapi import Request, status
from fastapi.responses import RedirectResponse
from functools import wraps

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def login_required(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if not request.session.get("user_id"):
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        return await func(request, *args, **kwargs)
    return wrapper

def role_admin_required(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        print("role dans la session: ",request.session.get('role') )
        if not request.session.get("user_id") or request.session.get("role") != "admin":
            request.session['unauthorize'] = {
                "status":"error",
                "message":"Vous n'êtes pas autorisé à acceder dans cette page"
            }
            return RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)
        return await func(request, *args, **kwargs)
    return wrapper

def role_adherent_required(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if not request.session.get("user_id") and request.session.get("role") != "adherent":
            return RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)
        return await func(request, *args, **kwargs)
    return wrapper


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
