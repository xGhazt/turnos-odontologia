from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PatientBase(BaseModel):
    """Campos compartidos de paciente con validación estricta."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    dni: str = Field(pattern=r"^\d{7,8}$")
    phone: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=150)
    birth_date: date | None = None
    insurance_provider: str | None = Field(default=None, max_length=100)
    insurance_number: str | None = Field(default=None, max_length=50)
    medical_history: str | None = None


class PatientCreate(PatientBase):
    """Schema para creación de paciente (POST /api/v1/patients)."""

    pass


class PatientUpdate(BaseModel):
    """Schema para actualización de contacto/cobertura (PUT /api/v1/patients/{id}).

    Excluye `dni` por regla de negocio (DNI es inmutable).
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=150)
    birth_date: date | None = None
    insurance_provider: str | None = Field(default=None, max_length=100)
    insurance_number: str | None = Field(default=None, max_length=50)
    medical_history: str | None = None


class PatientResponse(PatientBase):
    """Schema de respuesta de paciente con ID y timestamps de auditoría."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        from_attributes=True,
    )

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PatientListResponse(BaseModel):
    """Schema de listado paginado de pacientes."""

    model_config = ConfigDict(extra="forbid")

    items: list[PatientResponse]
    total: int
    page: int
    size: int
    total_pages: int
