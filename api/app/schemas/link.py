from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator


MAX_TAGS = 10
MAX_TAG_LENGTH = 32
ALLOWED_SCHEMES = {"http", "https"}


def normalize_and_validate_url(raw_value: str) -> str:
    trimmed = raw_value.strip()
    if not trimmed:
        raise ValueError("long_url must not be empty")

    if any(ord(char) < 32 or ord(char) == 127 for char in trimmed):
        raise ValueError("long_url must not contain control characters")

    if "\\" in trimmed:
        raise ValueError("long_url must use standard URL separators")

    parsed = urlsplit(trimmed)
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise ValueError("long_url scheme must be http or https")
    if not parsed.netloc or parsed.username or parsed.password:
        raise ValueError("long_url must be a direct http or https URL")
    if not parsed.hostname:
        raise ValueError("long_url must include a hostname")

    return trimmed


class LinkCreate(BaseModel):
    long_url: str
    expires_at: datetime | None = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("long_url")
    @classmethod
    def validate_long_url(cls, value: str) -> str:
        return normalize_and_validate_url(value)

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None

        comparison_target = value
        if value.tzinfo is None:
            comparison_target = value.replace(tzinfo=timezone.utc)

        if comparison_target <= datetime.now(timezone.utc):
            raise ValueError("expires_at must be in the future")
        return value

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str]) -> list[str]:
        if len(value) > MAX_TAGS:
            raise ValueError(f"tags must contain at most {MAX_TAGS} items")

        normalized: list[str] = []
        for tag in value:
            cleaned = tag.strip()
            if not cleaned:
                raise ValueError("tags must not be empty")
            if len(cleaned) > MAX_TAG_LENGTH:
                raise ValueError(
                    f"each tag must be at most {MAX_TAG_LENGTH} characters long"
                )
            normalized.append(cleaned)
        return normalized


class LinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    long_url: str
    created_by: str
    created_at: datetime
    expires_at: datetime | None = None
    tags: list[str] = Field(default_factory=list)


class LinkCreateResponse(BaseModel):
    id: int
    code: str
    short_url: str
    long_url: str
    created_at: datetime


class LinkListResponse(BaseModel):
    items: list[LinkRead]
    limit: int
    offset: int
    total: int


def build_link_create_response(link: Any, short_url: str) -> LinkCreateResponse:
    return LinkCreateResponse(
        id=link.id,
        code=link.code,
        short_url=short_url,
        long_url=link.long_url,
        created_at=link.created_at,
    )
