import enum

from sqlalchemy import Column, Integer, String, DateTime, func, Enum, ForeignKey
from sqlalchemy.orm import relationship

from src.database import Base

#Modeles Users
class UserRole(str, enum.Enum):
    ADHERENT = "adherent"
    ADMIN = "admin"

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDRE = "suspendre"
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.ADHERENT, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    livres = relationship("Emprunt", back_populates="adherents",cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="adherents",cascade="all, delete-orphan")

#Modele Livres
class Livre(Base):
    __tablename__ = "livres"
    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String, nullable=False)
    description = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    stock = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    emprunts = relationship("Emprunt", back_populates="livres", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="livres", cascade="all, delete-orphan")


#Modèle Emprunts
class Emprunt(Base):
    __tablename__ = "emprunts"
    id = Column(Integer, primary_key=True, index=True)
    id_livre = Column(Integer, ForeignKey("livres.id", ondelete="CASCADE"))
    id_adherent = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date_emprunt = Column(DateTime(timezone=True))
    date_retour_prevue = Column(DateTime(timezone=True))
    date_retour_effectif = Column(DateTime(timezone=True))
    livres = relationship("Livre", back_populates="emprunts")
    adherents = relationship("User", back_populates="livres")

#Modele Reservation
class StatusReservation(str, enum.Enum):
    CONFIRMER = "confirmer"
    EMPRUNTER = "emprunter"
    RETOURNER = "retourner"
    ANNULER = "annuler"

class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    id_livre = Column(Integer, ForeignKey("livres.id", ondelete="CASCADE"))
    id_adherent = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date_reservation = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(StatusReservation), default=StatusReservation.CONFIRMER)
    livres = relationship("Livre", back_populates="reservations")
    adherents = relationship("User", back_populates="reservations")

