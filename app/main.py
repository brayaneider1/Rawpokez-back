"""
app/main.py — Punto de entrada de la aplicación FastAPI.
Configuración de CORS, Middlewares y registro de todos los Routers.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.routers import designs, quotations, bookings, uploads
from app.routers import waitlist, products, orders, leads, ai, notifications, blog

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="RAWPOKEZ Backend API",
    description="Backend en FastAPI para el estudio de tatuajes Handpoke de María — Florencia, Caquetá",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers existentes ───────────────────────────────────────────────────────
app.include_router(designs.router,      prefix="/api/v1/designs",       tags=["Designs"])
app.include_router(quotations.router,   prefix="/api/v1/quotations",    tags=["Quotations"])
app.include_router(bookings.router,     prefix="/api/v1/bookings",      tags=["Bookings"])
app.include_router(uploads.router,      prefix="/api/v1/uploads",       tags=["Uploads"])

# ─── Nuevos routers ───────────────────────────────────────────────────────────
app.include_router(waitlist.router,     prefix="/api/v1/waitlist",      tags=["Waitlist"])
app.include_router(products.router,     prefix="/api/v1/products",      tags=["Store"])
app.include_router(orders.router,       prefix="/api/v1/orders",        tags=["Store"])
app.include_router(leads.router,        prefix="/api/v1/leads",         tags=["CRM"])
app.include_router(ai.router,           prefix="/api/v1/ai",            tags=["AI"])
app.include_router(notifications.router,prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(blog.router,         prefix="/api/v1/blog",          tags=["Blog"])


@app.get("/health", tags=["System"])
async def health_check():
    """Health check para monitorizar si la app está viva."""
    return {"status": "ok", "environment": settings.app_env, "version": "2.0.0"}
