import re
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from core.exceptions import (
    InvalidURLError,
    ResourceNotFoundError,
    ValidationError,
)
from core.logger import log
from models import Resource, ResourceStatus, Tag
from repositories.category_repo import CategoryRepository
from repositories.resource_repo import ResourceRepository
from repositories.tag_repo import TagRepository
from .scraper_service import ScraperService

_URL_RE = re.compile(
    r"^https?://"
    r"([\w\-]+\.)+[\w\-]+"
    r"(:\d+)?"
    r"(/[\w\-./?%&=#@!$&'()*+,;:]*)?"
    r"$",
    re.IGNORECASE,
)

_PLATFORM_TAGS = {
    "youtube.com": "youtube",
    "youtu.be": "youtube",
    "linkedin.com": "linkedin",
    "instagram.com": "instagram",
    "github.com": "github",
    "x.com": "twitter",
    "twitter.com": "twitter",
    "medium.com": "medium",
    "substack.com": "substack",
    "reddit.com": "reddit",
}


def _validate_url(url: str) -> None:
    if not _URL_RE.match(url):
        raise InvalidURLError(f"Gecersiz URL formati: {url!r}")


def _normalize_tag_names(tag_names: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for tag_name in tag_names:
        name = tag_name.lower().strip()
        if name and name not in seen:
            normalized.append(name)
            seen.add(name)
    return normalized


def _url_tag_names(url: str | None) -> list[str]:
    if not url:
        return []

    host = (urlparse(url).hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if host.startswith("m."):
        host = host[2:]

    for suffix, tag_name in _PLATFORM_TAGS.items():
        if host == suffix or host.endswith(f".{suffix}"):
            return [tag_name]

    parts = [part for part in host.split(".") if part]
    if len(parts) >= 2:
        return [parts[-2]]
    return parts[:1]


def _merge_tag_names(tag_names: list[str], url: str | None) -> list[str]:
    return _normalize_tag_names([*tag_names, *_url_tag_names(url)])


def _status_for_progress(progress: float) -> ResourceStatus:
    if progress >= 100:
        return ResourceStatus.COMPLETED
    if progress > 0:
        return ResourceStatus.IN_PROGRESS
    return ResourceStatus.PLANNED


def _progress_for_status(status: ResourceStatus, current_progress: float) -> float:
    if status in (ResourceStatus.INBOX, ResourceStatus.PLANNED):
        return 0.0
    if status == ResourceStatus.COMPLETED:
        return 100.0
    if status == ResourceStatus.IN_PROGRESS:
        return current_progress if 0.0 < current_progress < 100.0 else 25.0
    return current_progress


class ResourceService:

    def __init__(self, session: Session) -> None:
        self._session = session
        self._resource_repo = ResourceRepository(session)
        self._tag_repo = TagRepository(session)
        self._category_repo = CategoryRepository(session)
        self._scraper = ScraperService()

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

        extra_metadata = self._resolve_extra_metadata(
            url=url,
            provided=data.get("extra_metadata"),
            scrape=bool(url),
            fallback=None,
        )

        initial_status = data.get("status", ResourceStatus.PLANNED)

        resource = Resource(
            title=title,
            url=url or None,
            category_id=category_id,
            status=initial_status,
            priority=priority,
            progress=_progress_for_status(initial_status, 0.0),
            content=data.get("content"),
            extra_metadata=extra_metadata,
        )

        # Once resource'u session'a ekle, sonra etiketleri bagla.
        # Bu sayede flush sirasinda relationship tam olarak cozumlenir.
        try:
            self._session.add(resource)
            self._session.flush()  # ID atanir, iliski tablosu hazir olur

            resource.tags = self._get_or_create_tags(
                _merge_tag_names(data.get("tag_names", []), url)
            )

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
            if "progress" not in data:
                resource.progress = _progress_for_status(resource.status, resource.progress)

        if "progress" in data:
            progress = float(data["progress"])
            if not (0.0 <= progress <= 100.0):
                raise ValueError("Ilerleme degeri 0-100 arasinda olmalidir.")
            resource.progress = progress
            resource.status = _status_for_progress(progress)

        if "priority" in data:
            priority = int(data["priority"])
            if priority not in (1, 2, 3):
                raise ValidationError("Oncelik degeri 1, 2 veya 3 olmalidir.")
            resource.priority = priority

        if "content" in data:
            resource.content = data["content"]

        if "is_pinned" in data:
            resource.is_pinned = bool(data["is_pinned"])

        if resource.url and ("url" in data or "extra_metadata" in data):
            resource.extra_metadata = self._resolve_extra_metadata(
                url=resource.url,
                provided=data.get("extra_metadata"),
                scrape=True,
                fallback=resource.extra_metadata,
            )
        elif "extra_metadata" in data:
            resource.extra_metadata = data["extra_metadata"]

        try:
            if "tag_names" in data or "url" in data:
                base_tag_names = (
                    data["tag_names"]
                    if "tag_names" in data
                    else [tag.name for tag in resource.tags]
                )
                resource.tags = self._get_or_create_tags(
                    _merge_tag_names(base_tag_names, resource.url)
                )
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
        resource.status = _status_for_progress(progress)

        if progress >= 100.0:
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

    def _resolve_extra_metadata(
        self,
        *,
        url: str | None,
        provided: dict | None,
        scrape: bool,
        fallback,
    ):
        """add ve update arasinda paylasilan extra_metadata cozumleyici.

        - url + scrape: scraper sonucu + provided dict varsa onu uzerine ezer.
        - url yok ama provided varsa: provided dondurulur.
        - aksi halde fallback (mevcut resource degeri ya da None).
        """
        if url and scrape:
            scraped = self._scraper.extract_metadata(url)
            if isinstance(provided, dict):
                return {**scraped, **provided}
            return scraped
        if isinstance(provided, dict):
            return provided
        return fallback

    def _get_or_create_tags(self, tag_names: list[str]) -> list[Tag]:
        tags: list[Tag] = []
        for normalized in _normalize_tag_names(tag_names):
            tag = self._tag_repo.get_by_name(normalized)
            if tag is None:
                tag = Tag(name=normalized)
                self._session.add(tag)
                self._session.flush()
            tags.append(tag)
        return tags
