from app.repositories.base import BaseRepository
from app.repositories.Chair import ChairRepository
from app.repositories.Patient import PatientRepository
from app.repositories.Professional import ProfessionalRepository
from app.repositories.User import UserRepository


__all__ = [
    "BaseRepository",
    "UserRepository",
    "ProfessionalRepository",
    "ChairRepository",
    "PatientRepository",
]