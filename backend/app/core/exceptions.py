from fastapi import HTTPException, status


class ConflictException(HTTPException):
    """Excepción para conflictos de negocio (HTTP 409)."""

    def __init__(self, detail: str = "Conflicto de recursos"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class NotFoundException(HTTPException):
    """Excepción para recursos no encontrados o inactivos (HTTP 404)."""

    def __init__(self, detail: str = "Recurso no encontrado"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
