## 1. Infraestructura de Modelos y Mixins

- [x] 1.1 Crear archivo `backend/app/models/base.py` con la clase `Base` y `AuditMixin`.
- [x] 1.2 Implementar decorador o evento de SQLAlchemy para actualizar `updated_at` automÃ¡ticamente.

## 2. DefiniciÃ³n de Entidades de Dominio

- [x] 2.1 Crear `backend/app/models/User.py` con modelos `User` y `Role`.
- [x] 2.2 Crear `backend/app/models/Professional.py` con el modelo `Professional` vinculado a `User`.
- [x] 2.3 Crear `backend/app/models/Chair.py` con el modelo `Chair` (box de atenciÃ³n).
- [x] 2.4 Exportar todos los modelos en `backend/app/models/__init__.py`.

## 3. PatrÃ³n Repository

- [x] 3.1 Implementar `backend/app/repositories/base.py` con `BaseRepository` genÃ©rico.
- [x] 3.2 Implementar repositorios especÃ­ficos: `UserRepository`, `ProfessionalRepository`, `ChairRepository`.

## 4. Persistencia y Datos Iniciales

- [x] 4.1 Generar primera migraciÃ³n de Alembic.
- [x] 4.2 Ejecutar migraciÃ³n: alembic upgrade head.
- [x] 4.3 Crear script de seed backend/scripts/seed.py con datos ficticios para Roles, Admin, Profesional y Box.
- [x] 5.1 Crear tests en `backend/tests/test_models.py` para validar creaciÃ³n y auditorÃ­a.
- [x] 5.2 Crear tests en `backend/tests/test_repositories.py` para validar operaciones CRUD.
- [x] 5.3 Ejecutar suite de tests completa: `pytest backend/tests`.
