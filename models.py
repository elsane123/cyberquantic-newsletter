"""
CyberQuantic Weekly — Modèles de données
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CQUseCase(BaseModel):
    id: str
    name: str
    description: str = ''
    sector: str = ''
    function: str = ''
    goal: str = ''
    roi: str = ''
    targetAudiences: List[str] = []


class CQCompany(BaseModel):
    id: str
    title: str
    description: str = ''
    country: str = ''
    website: str = ''
    capabilities: List[str] = []
    industry: List[str] = []


class CQApi(BaseModel):
    id: str
    title: str
    description: str = ''
    website: str = ''
    capabilities: List[str] = []


class CQPrompt(BaseModel):
    id: str
    title: str
    description: str = ''
    function: str = ''


class NewsletterContext(BaseModel):
    """Contexte complet transmis de Agent1 → Agent2"""
    date_str: str                          # ex: "Lundi 14 Avril 2026"
    date_iso: str                          # ex: "2026-04-14"
    week_number: int
    use_case: CQUseCase
    company: CQCompany
    api: CQApi
    prompt: CQPrompt
    blog_use_case: CQUseCase              # use case distinct pour l'article blog
    eu_ai_act_tip: str = ''               # insight EU AI Act de la semaine
    ai_stat: str = ''                     # statistique IA de la semaine


class NewsletterDraft(BaseModel):
    """Brouillon généré par Agent2, transmis à Agent3"""
    date_str: str
    date_iso: str
    subject: str
    preheader: str = ''
    html_body: str
    text_body: str = ''
    blog_html: str = ''
    blog_title: str = ''
    blog_slug: str = ''
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class PublicationResult(BaseModel):
    success: bool
    newsletter_url: Optional[str] = None
    blog_url: Optional[str] = None
    subscribers_count: int = 0
    emails_sent: int = 0
    error: Optional[str] = None
    published_at: Optional[datetime] = None
