from sqlalchemy import select

from app.db import SessionLocal
from app.models import Link


def main() -> None:
    inserted_code = "abc123"
    long_url = "https://example.com"

    with SessionLocal() as session:
        existing = session.scalar(select(Link).where(Link.code == inserted_code))
        if existing is None:
            existing = Link(
                code=inserted_code,
                long_url=long_url,
                created_by="module-02-seed",
            )
            session.add(existing)
            session.commit()
            session.refresh(existing)

        matched = session.scalar(select(Link).where(Link.code == inserted_code))
        if matched is None:
            raise RuntimeError("Query-by-code failed to find the seeded link.")

        print(f"inserted code: {inserted_code}")
        print(f"selected code: {matched.code}")
        print(f"matched long_url: {matched.long_url}")


if __name__ == "__main__":
    main()
