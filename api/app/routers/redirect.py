import logging

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db_session
from app.logging_config import log_event
from app.services.links_service import get_link_by_code


router = APIRouter(tags=["redirect"])


@router.get("/r/{code}", status_code=307)
def redirect_by_code(code: str, db_session: Session = Depends(get_db_session)) -> RedirectResponse:
    link = get_link_by_code(db_session, code)
    
    # FIXED: Atomic upsert that eliminates BOTH race conditions
    # 1. Prevents duplicate insert (first race)
    # 2. Ensures last_accessed_at always reflects the actual last request (second race)
    
    # Single atomic operation using database time (now())
    # This ensures no Python-to-database timing window exists
    db_session.execute(
        text("""
            INSERT INTO click_events (link_id, clicked_at, last_accessed_at)
            VALUES (:link_id, now(), now())
            ON CONFLICT (link_id)
            DO UPDATE SET last_accessed_at = now()
        """),
        {"link_id": link.id}
    )
    db_session.commit()
    
    log_event(logging.INFO, "redirect executed", short_code=code)
    return RedirectResponse(url=link.long_url, status_code=307)


