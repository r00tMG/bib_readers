from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr

from src.models import UserRole, UserStatus, StatusReservation


# Mapper du modele User
class User(BaseModel):
    fullname: str
    email:EmailStr
    password:str
    role:UserRole
    confirm_password:str
    status:UserStatus
    created_at:datetime

class UserResponse(BaseModel):
    id : int
    fullname: str
    email: EmailStr
    role: UserRole
    created_at: datetime
    status: UserStatus
    class Config:
        use_enum_values = True
        from_attributes = True

#Mapper du modele Livre
class Livre(BaseModel):
    id:int
    titre:str
    description:str
    image_url : str
    stock:int
    rating:str

class LivreResponse(BaseModel):
    id:int
    titre:str
    description:str
    image_url : str
    stock:int
    rating:int
    created_at:datetime
    class Config:
        from_attributes = True

#DTO du modele Emprunt
#emprunts(id, id_adherent, id_livre, date_emprunt, date_retour_prevue, date_retour_effectif)
class Emprunt(BaseModel):
    id : int
    id_adherent: int
    id_livre:int
    date_emprunt: datetime
    date_retour_prevue: datetime
    date_retour_effectif: datetime

class EmpruntResponse(BaseModel):
    id : int
    adherents: List[UserResponse]
    livres: List[LivreResponse]
    date_emprunt: datetime
    date_retour_prevue: datetime
    date_retour_effectif: datetime
    class Config:
        from_attributes = True

#DTO du modele Reservation
##reservations(id, id_adherent, id_livre, date_reservation, statut)
class Reservation(BaseModel):
    id: int
    id_adherent: int
    id_livre: int
    date_reservation: datetime
    status: str


class ReservationResponse(BaseModel):
    id: int
    adherents: List[UserResponse]
    livres: List[LivreResponse]
    date_reservation: datetime
    status: StatusReservation
    class Config:
        use_enum_values = True
        from_attributes = True
