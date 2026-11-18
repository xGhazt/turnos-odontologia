"""Seed inicial de datos ficticios para C-02 core-models.

Este script crea datos 100% ficticios para el setup inicial del sistema.
Está diseñado para ser idempotente: ejecutarlo múltiples veces no debería
romper nada ni insertar duplicados.

Utiliza el mecanismo de sesiones asíncronas existente del proyecto (db.py).
"""

from sqlalchemy import select

from app.core.db import get_session_factory
from app.models.Chair import Chair
from app.models.Professional import Professional
from app.models.User import Role, User

# Hashes simulados bcrypt (formato $2b$...) - 100% ficticios según RN-06
SIMULATED_HASHES = {
    "password123": "$2b$12$CfGKXvIhQeM0l.lxSMy1juuM6vywT6.k5qCvNQ.OGZoTjQJqj2WuC",
    "admin123": "$2a$12$LnGmO6F5xYwFbEH2lXyK/uKJiSggdTJJZ8T.zx.Y.L5YkOQ.kS6Cu",
}


# ————————————————————————————————————————————————————————————————————
# get_or_create corregido:
# - Separa search_by (para SELECT) de create_by (para model()).
# - NO atrapa IntegrityError: la excepción propaga para que la transacción
#   completa haga rollback. El caller decide qué hacer con el error.
# ————————————————————————————————————————————————————————————————————

async def get_or_create(session, model, *, search_by: dict, create_by: dict) -> tuple:
    """Obtener o crear un registro de forma asíncrona e idempotente.

    Separa claramente los campos de búsqueda de los campos de creación.

    Args:
        session: AsyncSession del proyecto.
        model: Clase SQLAlchemy model.
        search_by: Diccionario de campos para el SELECT (condiciones únicas).
        create_by: Diccionario de campos para instanciar el modelo al crear.

    Returns:
        tuple (instance, created) donde created=True si fue creado nuevo,
        False si ya existía.

    Raises:
        IntegrityError: Si hay violación de restricción única (por ejemplo,
            intento insertar un duplicado de email/registration_name). La
            excepción propaga al caller para que la transacción se revoque.
    """
    # 1. Búsqueda: solo los campos para filtrar (campos con restricción única)
    stmt = select(model).filter_by(**search_by)
    result = await session.execute(stmt)
    instance = result.scalar_one_or_none()

    if instance is not None:
        # Registro existente encontrado — no crear nada nuevo
        return instance, False

    # 2. Creación: instanciar con create_by (campos para el modelo nuevo)
    instance = model(**create_by)
    session.add(instance)

    # Flush inmediato para garantizar que el instance tenga ID asignado
    # antes de que el caller asigne relaciones (role_id, user_id, etc.).
    # No atrapamos IntegrityError: si hay violación de restricción única,
    # la excepción propaga y la transacción padre hará rollback.
    await session.flush()

    return instance, True


# ————————————————————————————————————————————————————————————————————
# Helpers específicos por entidad
# ————————————————————————————————————————————————————————————————————

async def _get_or_create_user(session, model, *, email: str, password_hash: str, role_id: int) -> tuple:
    """Obtener o crear un User buscando por email único."""
    stmt = select(model).filter_by(email=email)
    result = await session.execute(stmt)
    instance = result.scalar_one_or_none()

    if instance is not None:
        return instance, False

    instance = model(
        email=email,
        password_hash=password_hash,
        role_id=role_id,
    )
    session.add(instance)
    await session.flush()
    return instance, True


async def _get_or_create_professional(session, model, *, registration_number: str, specialty: str, user_id: int) -> tuple:
    """Obtener o crear un Professional buscando por registration_number único."""
    stmt = select(model).filter_by(registration_number=registration_number)
    result = await session.execute(stmt)
    instance = result.scalar_one_or_none()

    if instance is not None:
        return instance, False

    instance = model(
        registration_number=registration_number,
        specialty=specialty,
        user_id=user_id,
    )
    session.add(instance)
    await session.flush()
    return instance, True


# ————————————————————————————————————————————————————————————————————
# _get_or_create_chair:
# Respeta el índice único parcial del modelo Chair:
#   postgresql_where=text("is_active = true"),
# sqlite_where=text("is_active = 1").
#
# Significado:
#   - Por el mismo `name`, solo puede haber UNA fila con is_active=true.
#   - Pueden existir filas con el mismo name pero is_active=false.
#   - El comportamiento debe ser: si ya existe uno activo con ese name,
#     no hacer nada. Si existe uno inactivo, podemos actualizarlo a active.
#   - Evitar MultipleResultsFound buscando bien.
# ————————————————————————————————————————————————————————————————————

async def _get_or_create_chair(session, model, *, name: str, is_active: bool = True) -> tuple:
    """Obtener o crear un Chair respetando el índice único parcial.

    El modelo Chair tiene un índice único parcial:
      unique=True, postgresql_where=text("is_active = true").

    Lógica idempotente:
    1. Buscar un sillón activo con ese name.
    2. Si existe → devolverlo sin modificarlo.
    3. Si no existe uno activo, buscar sillones inactivos con ese name.
    4. Si hay inactivos, seleccionar el de menor ID y reactivarlo.
    5. Si ninguno existe, crear uno nuevo con is_active=is_active.
    """
    # 1. Buscar primero por name=name Y is_active=True
    stmt = select(model).filter_by(name=name, is_active=True)
    result = await session.execute(stmt)
    active_instance = result.scalar_one_or_none()

    if active_instance is not None:
        # Ya existe uno activo con ese name: devolver sin modificarlo
        return active_instance, False

    # 2. No hay activo: buscar inactivos con ese name
    stmt = select(model).filter_by(name=name, is_active=False)
    result = await session.execute(stmt)
    inactive_instances = result.scalars().all()

    if inactive_instances:
        # Seleccionar determinísticamente el de menor ID
        target = min(inactive_instances, key=lambda x: x.id)
        target.is_active = is_active
        await session.flush()
        return target, False

    # 3. Ningún registro con ese name existe: crear uno nuevo
    instance = model(name=name, is_active=is_active)
    session.add(instance)
    await session.flush()
    return instance, True


# ————————————————————————————————————————————————————————————————————
# Secuencia de seed
# ————————————————————————————————————————————————————————————————————

async def seed():
    """Ejecutar seed completo de forma asíncrona e idempotente.

    Secuencia estricta para garantizar IDs mediante flush():
    1. Roles (id por nombre) → flush
    2. Users (con role_id del role) → flush
    3. Professional (con user_id del user) → flush
    4. Chairs → flush final
    5. Commit transaccional

    Utiliza get_session_factory() del proyecto; no crea engine nuevo.
    No ejecuta metadata.create_all() - tablas vienen de migración 001.

    La función se ejecuta dentro de una única transacción async.
    Si ocurre cualquier excepción, el contexto async with hace rollback
    automático de todas las operaciones del seed.

    Returns un resumen distinguendo qué registros fueron creados vs yaexistentes.
    """
    factory = get_session_factory()
    summary = {
        "roles": {"created": 0, "existing": 0},
        "users": {"created": 0, "existing": 0},
        "professional": {"created": 0, "existing": 0},
        "chairs": {"created": 0, "existing": 0},
    }

    async with factory() as session:
        # =====================================================
        # PASO 1: Crear u obtener Roles
        # =====================================================
        roles_names = ["admin", "odontologo", "secretaria", "paciente"]
        role_instances = {}

        for role_name in roles_names:
            role, created = await get_or_create(
                session, Role,
                search_by={"name": role_name},
                create_by={"name": role_name},
            )
            role_instances[role_name] = role
            summary["roles"]["created"] += 1 if created else 0
            summary["roles"]["existing"] += 1 if not created else 0

        # =====================================================
        # PASO 2: Crear u obtener Usuarios
        # =====================================================
        # Ya tenemos role_instances con IDs garantizados vía flush del paso 1.

        # Usuario con rol Odontólogo (no Admin, según requisito C-02)
        odontologo_user, odont_created = await _get_or_create_user(
            session, User,
            email="dr.fernando.garcia@consultorio.ficticio",
            password_hash=SIMULATED_HASHES["password123"],
            role_id=role_instances["odontologo"].id,
        )
        summary["users"]["created"] += 1 if odont_created else 0
        summary["users"]["existing"] += 0 if odont_created else 1

        # Usuario adicional con rol Admin
        admin_user, admin_created = await _get_or_create_user(
            session, User,
            email="admin@consultorio.ficticio",
            password_hash=SIMULATED_HASHES["admin123"],
            role_id=role_instances["admin"].id,
        )
        summary["users"]["created"] += 1 if admin_created else 0
        summary["users"]["existing"] += 0 if admin_created else 1

        # =====================================================
        # PASO 3: Crear u obtener Professional
        # =====================================================
        # Vinculado al usuario Odontólogo; user_id ya garantizado
        professional, prof_created = await _get_or_create_professional(
            session, Professional,
            registration_number="M-12345",
            specialty="Ortodoncia",
            user_id=odontologo_user.id,
        )
        summary["professional"]["created"] += 1 if prof_created else 0
        summary["professional"]["existing"] += 0 if prof_created else 1

        # =====================================================
        # PASO 4: Crear u obtener Sillones (Chairs)
        # =====================================================
        # Los chairs usan índice partial unique sobre (name, is_active=true).
        # _get_or_create_chair maneja los casos activo/inactivo y MultipleResultsFound.
        for chair_name in ["Box 1", "Box 2"]:
            chair, chair_created = await _get_or_create_chair(
                session, Chair, name=chair_name, is_active=True,
            )
            summary["chairs"]["created"] += 1 if chair_created else 0
            summary["chairs"]["existing"] += 0 if chair_created else 1

        # =====================================================
        # PASO 5: Commit final
        # =====================================================
        # El contexto async with factory() hará commit al salir si no hubo excepción.
        # Pero somos explícitos para que sea claro:
        await session.commit()

    return summary


def run_seed():
    """Función síncrona de entrada que ejecuta el seed async.

    Obtiene una sesión del pool del proyecto, ejecuta la secuencia
    ordenada de creación de entidades y muestra un resumen.

    Idempotente: ejecutar varias veces produce mismo resultado sin errores.
    """
    import asyncio

    async def _run():
        try:
            summary = await seed()
            print("-" * 60)
            print("Seed inicial completado:")
            print(f"  Roles - Creados: {summary['roles']['created']}, Existentes: {summary['roles']['existing']}")
            print(f"  Usuarios - Creados: {summary['users']['created']}, Existentes: {summary['users']['existing']}")
            print(f"  Professional - Creado: {summary['professional']['created']}, Existente: {summary['professional']['existing']}")
            print(f"  Sillones - Creados: {summary['chairs']['created']}, Existentes: {summary['chairs']['existing']}")
            print("-" * 60)
        except Exception as e:
            # El contexto async with factory() hará rollback automático.
            # Relanzamos para que el caller se entere.
            print(f"Error durante seed: {e}")
            raise

    asyncio.run(_run())


if __name__ == "__main__":
    run_seed()