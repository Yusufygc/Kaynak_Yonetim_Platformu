import re
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from core.exceptions import (
    InvalidURLError,
    ResourceNotFoundError,
    ValidationError,
)
from core.logger import log
from models.resource import Resource, ResourceStatus
from repositories.category_repo import CategoryRepository
from repositories.resource_repo import ResourceRepository
from repositories.tag_repo import TagRepository

_URL_RE = re.compile(
    r"^(https?://)?"
    r"([\w\-]+\.)+[\w\-]+"
    r"(:\d+)?"
    r"(/[\w\-./?%&=]*)?"
    r"$",
    re.IGNORECASE,
)


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if not parsed.scheme or parsed.scheme not in ("http", "https"):
        raise InvalidURLError(f"Gecersiz URL formati: {url!r}")
    if not _URL_RE.match(url):
        raise InvalidURLError(f"Gecersiz URL formati: {url!r}")


class ResourceService:

    def __init__(self, session: Session) -> None:
        self._session = session
        self._resource_repo = ResourceRepository(session)
        self._tag_repo = TagRepository(session)
        self._category_repo = CategoryRepository(session)

    # ------------------------------------------------------------------ #
    # Okuma
    # ------------------------------------------------------------------ #

    def get_all(self) -> list[Resource]:
        return self._resource_repo.get_all()

    def get_by_id(self, resource_id: int) -> Resource:
        resource = self._resource_repo.get_by_id(resource_id)
        if resource is None:
            raise ResourceNotFoundError(f"Kaynak bulunamadi: id={resource_id}")
        return resource

    def get_by_status(self, status: ResourceStatus) -> list[Resource]:
        return self._resource_repo.get_by_status(status)

    def search(self, keyword: str) -> list[Resource]:
        return self._resource_repo.search_by_keyword(keyword)

    def get_by_category(self, category_id: int) -> list[Resource]:
        return self._resource_repo.get_by_category(category_id)

    def get_urls_only(self) -> list[Resource]:
        return self._resource_repo.get_urls_only()

    # ------------------------------------------------------------------ #
    # Yazma
    # ------------------------------------------------------------------ #

    def add_new_resource(self, data: dict) -> Resource:
        """
        Beklenen data anahtarlari:
          title (str, zorunlu), url (str, opsiyonel),
          category_id (int, opsiyonel), status (ResourceStatus, opsiyonel),
          priority (int, opsiyonel), content (str, opsiyonel),
          tag_names (list[str], opsiyonel), extra_metadata (dict, opsiyonel)
        """
        title = (data.get("title") or "").strip()
        if not title:
            raise ValidationError("Baslik bos olamaz.")

        url = data.get("url")
        if url:
            url = url.strip()
            _validate_url(url)

        category_id = data.get("category_id")
        if category_id is not None:
            if self._category_repo.get_by_id(category_id) is None:
                raise ResourceNotFoundError(f"Kategori bulunamadi: id={category_id}")

        priority = int(data.get("priority", 2))
        if priority not in (1, 2, 3):
            raise ValidationError("Oncelik degeri 1, 2 veya 3 olmalidir.")

        resource = Resource(
            title=title,
            url=url or None,
            category_id=category_id,
            status=data.get("status", ResourceStatus.PLANNED),
            priority=priority,
            progress=0.0,
            content=data.get("content"),
            extra_metadata=data.get("extra_metadata"),
        )

        # Once resource'u session'a ekle, sonra etiketleri bagla.
        # Bu sayede flush sirasinda relationship tam olarak cozumlenir.
        try:
            self._session.add(resource)
            self._session.flush()  # ID atanir, iliski tablosu hazir olur

            tag_names: list[str] = data.get("tag_names", [])
            from models.tag import Tag as TagModel
            for tag_name in tag_names:
                normalized = tag_name.lower().strip()
                tag = self._tag_repo.get_by_name(normalized)
                if tag is None:
                    tag = TagModel(name=normalized)
                    self._session.add(tag)
                    self._session.flush()
                resource.tags.append(tag)

            self._session.commit()
            log.info("Yeni kaynak eklendi: id=%d title=%r", resource.id, resource.title)
        except Exception:
            self._session.rollback()
            log.exception("Kaynak eklenirken hata olustu.")
            raise

        return resource

    def update_resource(self, resource_id: int, data: dict) -> Resource:
        resource = self.get_by_id(resource_id)

        if "title" in data:
            title = data["title"].strip()
            if not title:
                raise ValidationError("Baslik bos olamaz.")
            resource.title = title

        if "url" in data:
            url = (data["url"] or "").strip()
            if url:
                _validate_url(url)
            resource.url = url or None

        if "category_id" in data:
            cat_id = data["category_id"]
            if cat_id is not None and self._category_repo.get_by_id(cat_id) is None:
                raise ResourceNotFoundError(f"Kategori bulunamadi: id={cat_id}")
            resource.category_id = cat_id

        if "status" in data:
            resource.status = data["status"]

        if "priority" in data:
            priority = int(data["priority"])
            if priority not in (1, 2, 3):
                raise ValidationError("Oncelik degeri 1, 2 veya 3 olmalidir.")
            resource.priority = priority

        if "content" in data:
            resource.content = data["content"]

        if "is_pinned" in data:
            resource.is_pinned = bool(data["is_pinned"])

        if "extra_metadata" in data:
            resource.extra_metadata = data["extra_metadata"]

        try:
            self._resource_repo.update(resource)
            self._session.commit()
            log.info("Kaynak guncellendi: id=%d", resource_id)
        except Exception:
            self._session.rollback()
            log.exception("Kaynak guncellenirken hata olustu.")
            raise

        return resource

    def update_resource_progress(self, resource_id: int, progress: float) -> Resource:
        if not (0.0 <= progress <= 100.0):
            raise ValueError("Ilerleme degeri 0-100 arasinda olmalidir.")

        resource = self.get_by_id(resource_id)
        resource.progress = progress

        if progress >= 100.0:
            resource.status = ResourceStatus.COMPLETED
            log.info("Kaynak tamamlandi: id=%d", resource_id)

        try:
            self._resource_repo.update(resource)
            self._session.commit()
        except Exception:
            self._session.rollback()
            log.exception("Ilerleme guncellenirken hata olustu.")
            raise

        return resource

    def delete_resource(self, resource_id: int) -> None:
        deleted = self._resource_repo.delete(resource_id)
        if not deleted:
            raise ResourceNotFoundError(f"Kaynak bulunamadi: id={resource_id}")
        try:
            self._session.commit()
            log.info("Kaynak silindi: id=%d", resource_id)
        except Exception:
            self._session.rollback()
            raise
