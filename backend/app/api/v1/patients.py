from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.repositories.Patient import PatientRepository
from app.schemas.patient import (
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)
from app.services.patient import PatientService

router = APIRouter(prefix="/patients", tags=["patients"])


def get_patient_service(session: AsyncSession = Depends(get_session)) -> PatientService:
    """Dependency injection para el servicio de pacientes."""
    repo = PatientRepository(session)
    return PatientService(repo)


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    data: PatientCreate,
    service: PatientService = Depends(get_patient_service),
) -> PatientResponse:
    """Crea un nuevo paciente con validación de DNI único (RN-04)."""
    patient = await service.create(data)
    return PatientResponse.model_validate(patient)


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    service: PatientService = Depends(get_patient_service),
) -> PatientResponse:
    """Obtiene la ficha de un paciente por su ID."""
    patient = await service.get_by_id(patient_id)
    return PatientResponse.model_validate(patient)


@router.get("", response_model=PatientListResponse)
async def list_patients(
    query: Optional[str] = Query(None, description="Búsqueda por DNI, apellido o nombre"),
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(20, ge=1, le=100, description="Tamaño de página"),
    service: PatientService = Depends(get_patient_service),
) -> PatientListResponse:
    """Listado paginado de pacientes con filtro de búsqueda opcional."""
    return await service.list(query=query, page=page, size=size)


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    data: PatientUpdate,
    service: PatientService = Depends(get_patient_service),
) -> PatientResponse:
    """Actualiza los datos de un paciente (excluyendo DNI)."""
    patient = await service.update(patient_id, data)
    return PatientResponse.model_validate(patient)
