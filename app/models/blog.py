"""
app/models/blog.py — Modelo para los artículos del blog.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional

def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

class BlogPostBase(SQLModel):
    title: str
    slug: str = Field(index=True, unique=True)
    excerpt: Optional[str] = None
    content: str  # Markdown or HTML content
    featured_image_url: Optional[str] = None
    is_published: bool = Field(default=False)

class BlogPost(BlogPostBase, table=True):
    __tablename__ = "blog_post"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

class BlogPostCreate(BlogPostBase):
    pass

class BlogPostUpdate(SQLModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    featured_image_url: Optional[str] = None
    is_published: Optional[bool] = None

class BlogPostRead(BlogPostBase):
    id: int
    created_at: datetime
    updated_at: datetime
