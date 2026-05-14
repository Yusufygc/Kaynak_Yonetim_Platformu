from sqlalchemy.orm import Session

from core.exceptions import DuplicateRecordError
from core.logger import log
from models.tag import Tag
from repositories.tag_repo import TagRepository


class TagService:

    def __init__(self, session: Session) -> None:
        self._session = session
        self._repo = TagRepository(session)

    def get_or_create_tag(self, name: str) -> Tag:
        """Varsa getir, yoksa olustur ve getir."""
        normalized = name.lower().strip()
        existing = self._repo.get_by_name(normalized)
        if existing:
            return existing
        tag = Tag(name=normalized)
        self._repo.create(tag)
        self._session.commit()
        log.info("Yeni etiket olusturuldu: %r", normalized)
        return tag

    def get_all(self) -> list[Tag]:
        return self._repo.get_all()

    def delete_tag(self, tag_id: int) -> None:
        deleted = self._repo.delete(tag_id)
        if not deleted:
            from core.exceptions import ResourceNotFoundError
            raise ResourceNotFoundError(f"Etiket bulunamadi: id={tag_id}")
        self._session.commit()
        log.info("Etiket silindi: id=%d", tag_id)
