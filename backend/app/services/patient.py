import math
from typing import Optional

from app.core.exceptions import ConflictException, NotFoundException
from app.models.Patient import Patient
from app.repositories.Patient import PatientRepository
from app.schemas.patient import PatientCreate, PatientListResponse, PatientResponse, PatientUpdate


class PatientService:
    """Servicio de dominio para la gestión del padrón de pacientes."""

    def __init__(self, repo: PatientRepository) -> None:
        self.repo = repo

    async def create(self, data: PatientCreate) -> Patient:
        """Crea un nuevo paciente validando unicidad de DNI (RN-04)."""
        existing = await self.repo.get_by_dni(data.dni)
        if existing is not None:
            raise ConflictException(detail="DNI ya registrado")

        return await self.repo.create(**data.model_dump())

    async def get_by_id(self, patient_id: int) -> Patient:
        """Obtiene un paciente activo por ID."""
        patient = await self.repo.get_by_id(patient_id)
        if patient is None or not patient.is_active:
            raise NotFoundException(detail="Paciente no encontrado")
        return patient

    async def list(
        self,
        query: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> PatientListResponse:
        """Lista pacientes con paginación y búsqueda por ILIKE."""
        items, total = await self.repo.search(query=query, page=page, size=size)
        total_pages = math.ceil(total / size) if total > 0 else 0
        return PatientListResponse(
            items=[PatientResponse.model_validate(p) for p in items],
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
        )

    async def update(self, patient_id: int, data: PatientUpdate) -> Patient:
        """Actualiza datos de contacto o cobertura médica de un paciente.

        Excluye DNI (inmutable por regla de negocio).
        """
        patient = await self.repo.get_by_id(patient_id)
        if patient is None or not patient.is_active:
            raise NotFoundException(detail="Paciente no encontrado")

        update_dict = data.model_dump(exclude_unset=True, exclude={"dni"})
        if not update_dict:
            return patient

        updated_patient = await self.repo.update(patient_id, **update_dict)
        return updated_patient
