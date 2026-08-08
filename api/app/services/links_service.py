import logging
import secrets
import string

from fastapi import HTTPException
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.logging_config import log_event
from app.models import Link
from app.schemas.link import LinkCreate

CODE_ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6
MAX_CODE_GENERATION_ATTEMPTS = 10


def build_short_url(base_url: str, code: str) -> str:
    return f"{base_url}/r/{code}"


def list_links(db_session: Session, *, limit: int, offset: int) -> tuple[list[Link], int]:
    query: Select[tuple[Link]] = (
        select(Link).order_by(Link.created_at.desc(), Link.id.desc()).limit(limit).offset(offset)
    )
    items = list(db_session.scalars(query))
    total = db_session.scalar(select(func.count()).select_from(Link)) or 0
    return items, total


def get_link_by_id(db_session: Session, link_id: int) -> Link:
    link = db_session.get(Link, link_id)
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return link


def get_link_by_code(db_session: Session, code: str) -> Link:
    link = db_session.scalar(select(Link).where(Link.code == code))
    if link is None:
        log_event(
            logging.ERROR,
            "link not found",
            short_code=code,
            status=404,
        )
        raise HTTPException(status_code=404, detail="Link not found")
    return link


def create_link(db_session: Session, payload: LinkCreate) -> Link:
    code = _generate_unique_code(db_session)
    link = Link(
        code=code,
        long_url=payload.long_url,
        created_by="public_consumer",
        expires_at=payload.expires_at,
        tags=payload.tags,
    )
    db_session.add(link)
    db_session.commit()
    db_session.refresh(link)
    return link


def _generate_unique_code(db_session: Session) -> str:
    for _ in range(MAX_CODE_GENERATION_ATTEMPTS):
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
        existing = db_session.scalar(select(Link.id).where(Link.code == code))
        if existing is None:
            return code
    raise RuntimeError("Unable to generate a unique short code")
