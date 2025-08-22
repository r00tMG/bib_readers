from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from routes import users, auth, home, gestion_adherents, livres
from src import models
from src.database import engine
from src.exceptions import validation_exception_handler_register, validation_exception_handler_login, \
    validation_exception_handler_modify, validation_exception_handler_update_livre

#Chargement de la base de données
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

#Chargement des fichiers statics
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


#Chargement des routes
app.include_router(users.routes)
app.include_router(auth.routes)
app.include_router(home.routes)
app.include_router(gestion_adherents.routes)
app.include_router(livres.routes)
#Chargement SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key="un_secret_key_tres_long")

#Charge des exceptions
app.add_exception_handler(RequestValidationError, validation_exception_handler_register)
app.add_exception_handler(RequestValidationError, validation_exception_handler_login)
app.add_exception_handler(RequestValidationError, validation_exception_handler_modify)
app.add_exception_handler(RequestValidationError, validation_exception_handler_update_livre)