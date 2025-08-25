#DTO du modele Reservation
##reservations(id, id_adherent, id_livre, date_reservation, statut)
from datetime import datetime
from typing import List

from pydantic import BaseModel

from src.models import StatusReservation
from src.schemas import UserResponse, LivreResponse


