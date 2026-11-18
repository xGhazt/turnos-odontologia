import asyncio
import os
import sys
from logging.config import fileConfig
from sqlalchemy.engine import make_url

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.settings import get_settings  # noqa: E402
from app.models.base import Base  # noqa: E402

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config


def _validate_postgresql_asyncpg(url: str) -> None:
    """Validates that the database URL uses the postgresql+asyncpg driver.

    Raises RuntimeError if the URL uses any other driver/dialect.
    Does NOT include the URL in error messages to avoid exposing credentials.
    """
    try:
        parsed = make_url(url)
    except Exception as e:
        raise RuntimeError(
            "URL de base de datos malformada. "
            "Verifique el formato de DATABASE_URL o settings.database_url."
        ) from e

    if parsed.drivername != "postgresql+asyncpg":
        raise RuntimeError(
            "Solo se permiten migraciones con PostgreSQL + asyncpg. "
            "Defina DATABASE_URL con postgresql+asyncpg://... o configurela en .env."
        )


def get_database_url() -> str:
    """Obtiene URL de BD para migraciones: prioriza env var, luego settings.

    Lanza RuntimeError si la URL no es postgresql+asyncpg (sin fallback a SQLite),
    para evitar silenciar errores de configuración de base de datos.

    Si DATABASE_URL está definida pero no es postgresql+asyncpg, se rechaza
    inmediatamente sin intentar leer settings.
    """
    url = os.environ.get("DATABASE_URL")
    if url:
        _validate_postgresql_asyncpg(url)
        return url
    try:
        from app.core.settings import get_settings
        settings = get_settings()
        if settings.database_url:
            _validate_postgresql_asyncpg(settings.database_url)
            return str(settings.database_url)
    except Exception as e:
        raise RuntimeError(
            "DATABASE_URL no configurada o inválida. "
            "Definila en el entorno o en .env basado en .env.example. "
            "Solo se permite postgresql+asyncpg para migraciones de producción."
        ) from e


config.set_main_option("sqlalchemy.url", get_database_url())

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
