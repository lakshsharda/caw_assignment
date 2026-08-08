import logging

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.db import get_db_session
from app.logging_config import log_event
from app.schemas.link import (
    LinkCreate,
    LinkCreateResponse,
    LinkListResponse,
    LinkRead,
    build_link_create_response,
)
from app.services.links_service import build_short_url, create_link, get_link_by_id, list_links


router = APIRouter(prefix="/links", tags=["links"])


@router.post("", response_model=LinkCreateResponse, status_code=status.HTTP_201_CREATED)
def create_link_route(
    payload: LinkCreate,
    request: Request,
    db_session: Session = Depends(get_db_session),
) -> LinkCreateResponse:
    link = create_link(db_session, payload)
    log_event(
        logging.INFO,
        "link created",
        short_code=link.code,
        url=payload.long_url,
    )
    short_url = build_short_url(str(request.base_url).rstrip("/"), link.code)
    return build_link_create_response(link, short_url)


@router.get("", response_model=LinkListResponse)
def list_links_route(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db_session: Session = Depends(get_db_session),
) -> LinkListResponse:
    items, total = list_links(db_session, limit=limit, offset=offset)
    return LinkListResponse(items=items, limit=limit, offset=offset, total=total)


@router.get("/{link_id}", response_model=LinkRead)
def get_link_by_id_route(
    link_id: int, db_session: Session = Depends(get_db_session)
) -> LinkRead:
    return get_link_by_id(db_session, link_id)
