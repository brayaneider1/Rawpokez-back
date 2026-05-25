"""
app/database.py — Motor async SQLModel + sesión de base de datos.
Provee `get_session` como dependency de FastAPI.
"""
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import get_settings

settings = get_settings()

# ─── Async engine (para la app en producción/dev) ─────────────────────────────
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env== "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,
)

async_session_factory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ─── Sync engine (solo para Alembic) ──────────────────────────────────────────
sync_engine = create_engine(
    settings.database_url_sync,
    echo=False,
)


async def get_session() -> AsyncSession:  # type: ignore[return]
    """Dependency de FastAPI — inyecta una sesión async por request."""
    async with async_session_factory() as session:
        yield session


async def create_db_and_tables() -> None:
    """Crea todas las tablas si no existen (usar solo en desarrollo)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
