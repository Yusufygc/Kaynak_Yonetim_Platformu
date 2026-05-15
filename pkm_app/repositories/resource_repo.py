from sqlalchemy import or_
from sqlalchemy.orm import Session

from models import Resource, ResourceStatus
from .base_repository import BaseRepository


class ResourceRepository(BaseRepository[Resource]):

    def __init__(self, session: Session) -> None:
        super().__init__(Resource, session)

    def get_by_status(self, status: ResourceStatus) -> list[Resource]:
        return (
            self._session.query(Resource)
            .filter(Resource.status == status)
            .all()
        )

    def search_by_keyword(self, keyword: str) -> list[Resource]:
        pattern = f"%{keyword}%"
        return (
            self._session.query(Resource)
            .filter(
                or_(
                    Resource.title.ilike(pattern),
                    Resource.url.ilike(pattern),
                    Resource.content.ilike(pattern),
                )
            )
            .all()
        )

    def get_with_tags(self, tag_ids: list[int]) -> list[Resource]:
        from models import resource_tags_link
        return (
            self._session.query(Resource)
            .join(resource_tags_link, Resource.id == resource_tags_link.c.resource_id)
            .filter(resource_tags_link.c.tag_id.in_(tag_ids))
            .distinct()
            .all()
        )

    def get_by_category(self, category_id: int) -> list[Resource]:
        return (
            self._session.query(Resource)
            .filter(Resource.category_id == category_id)
            .all()
        )

    def get_pinned(self) -> list[Resource]:
        return (
            self._session.query(Resource)
            .filter(Resource.is_pinned.is_(True))
            .order_by(Resource.created_at.desc())
            .all()
        )

    def get_urls_only(self) -> list[Resource]:
        """Sadece URL alani dolu kaynaklari dondurur (URL Vitrini icin)."""
        return (
            self._session.query(Resource)
            .filter(Resource.url.isnot(None), Resource.url != "")
            .all()
        )
