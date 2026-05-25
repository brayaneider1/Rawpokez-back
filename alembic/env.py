import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from sqlmodel import SQLModel

# Cargar configuración de la app
from app.config import get_settings

# Importar TODOS los modelos para que alembic los detecte (metadata)
from app.models.design import Design
from app.models.quotation import Quotation
from app.models.booking import Booking
from app.models.waitlist import WaitlistEntry
from app.models.product import Product
from app.models.order import Order
from app.models.lead import Lead
from app.models.push_subscription import PushSubscription
from app.models.settings import SiteSettings
from app.models.gallery import GalleryImage
from app.models.blog import BlogPost

settings = get_settings()
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    url = settings.database_url_sync
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
    configuration = config.get_section(config.config_ini_section, {})
    # Inyectar url dinámicamente desde el config.py
    configuration["sqlalchemy.url"] = settings.database_url
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
