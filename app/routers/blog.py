"""
app/routers/blog.py — Endpoints para gestionar artículos del blog.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List

from app.database import get_session
from app.models.blog import BlogPost, BlogPostCreate, BlogPostRead, BlogPostUpdate

router = APIRouter()

@router.get("/", response_model=List[BlogPostRead])
async def get_posts(
    session: AsyncSession = Depends(get_session),
    published_only: bool = True
):
    """Listar posts del blog."""
    query = select(BlogPost)
    if published_only:
        query = query.where(BlogPost.is_published == True)
    
    result = await session.execute(query)
    return result.scalars().all()

@router.get("/{slug}", response_model=BlogPostRead)
async def get_post_by_slug(
    slug: str,
    session: AsyncSession = Depends(get_session)
):
    """Obtener un post por su slug."""
    query = select(BlogPost).where(BlogPost.slug == slug)
    result = await session.execute(query)
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    return post

@router.post("/", response_model=BlogPostRead, status_code=201)
async def create_post(
    post_in: BlogPostCreate,
    session: AsyncSession = Depends(get_session)
):
    """Crear un nuevo post (admin)."""
    post = BlogPost.model_validate(post_in)
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post
