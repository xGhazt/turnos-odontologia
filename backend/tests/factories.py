"""Fábricas de datos ficticios para tests (RN-06 — sin datos reales de pacientes)."""

from datetime import date
from typing import Any


def make_patient_data(**overrides: Any) -> dict[str, Any]:
    """Genera datos ficticios válidos para crear un paciente."""
    data: dict[str, Any] = {
        "first_name": "Juan",
        "last_name": "Pérez",
        "dni": "12345678",
        "phone": "+54 11 4000-0001",
        "email": "juan.perez@fake.com",
        "birth_date": date(1990, 5, 15),
        "insurance_provider": "OSDE",
        "insurance_number": "999000111",
        "medical_history": "Sin antecedentes relevantes",
    }
    data.update(overrides)
    return data
