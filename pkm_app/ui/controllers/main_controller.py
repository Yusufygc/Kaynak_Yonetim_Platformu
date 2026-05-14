from sqlalchemy.orm import Session

from core.events import event_bus
from core.logger import log
from models.resource import Resource
from services.category_service import CategoryService
from services.resource_service import ResourceService
from services.tag_service import TagService


class MainController:
    """Arayüz olaylarini yakalar, Service katmanini cagirir, Event Bus'a sinyal fırlatir."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._resource_svc = ResourceService(session)
        self._category_svc = CategoryService(session)
        self._tag_svc = TagService(session)

        self._connect_events()

    def _connect_events(self) -> None:
        event_bus.search_query_changed.connect(self._on_search)

    # ------------------------------------------------------------------ #
    # Kaynak islemleri
    # ------------------------------------------------------------------ #

    def load_all_resources(self) -> list[Resource]:
        return self._resource_svc.get_all()

    def load_resources_by_filter(self, filter_key: str) -> list[Resource]:
        if filter_key == "all":
            return self._resource_svc.get_all()
        if filter_key == "url_showcase":
            return self._resource_svc.get_urls_only()
        if filter_key.startswith("category:"):
            cat_id = int(filter_key.split(":")[1])
            return self._resource_svc.get_by_category(cat_id)
        if filter_key.startswith("tag:"):
            tag_id = int(filter_key.split(":")[1])
            return self._resource_svc.search_by_tag([tag_id]) if hasattr(
                self._resource_svc, "search_by_tag"
            ) else []
        return self._resource_svc.get_all()

    def get_resource(self, resource_id: int) -> Resource | None:
        try:
            return self._resource_svc.get_by_id(resource_id)
        except Exception:
            log.exception("Kaynak getirilemedi: id=%d", resource_id)
            return None

    def add_resource(self, data: dict) -> Resource | None:
        try:
            resource = self._resource_svc.add_new_resource(data)
            event_bus.resource_added.emit(resource.id)
            return resource
        except Exception as exc:
            log.error("Kaynak eklenemedi: %s", exc)
            event_bus.error_occurred.emit(str(exc))
            return None

    def update_progress(self, resource_id: int, progress: float) -> None:
        try:
            self._resource_svc.update_resource_progress(resource_id, progress)
            event_bus.resource_updated.emit(resource_id)
        except Exception as exc:
            log.error("Ilerleme guncellenemedi: %s", exc)

    def delete_resource(self, resource_id: int) -> None:
        try:
            self._resource_svc.delete_resource(resource_id)
            event_bus.resource_deleted.emit(resource_id)
        except Exception as exc:
            log.error("Kaynak silinemedi: %s", exc)

    # ------------------------------------------------------------------ #
    # Kategori / Etiket
    # ------------------------------------------------------------------ #

    def load_categories(self) -> list:
        return self._category_svc.get_all()

    def load_tags(self) -> list:
        return self._tag_svc.get_all()

    # ------------------------------------------------------------------ #
    # Slot'lar
    # ------------------------------------------------------------------ #

    def _on_search(self, keyword: str) -> None:
        if not keyword.strip():
            results = self._resource_svc.get_all()
        else:
            results = self._resource_svc.search(keyword)
        # UI katmani bu sinyali dinleyerek kartlari yeniler
        event_bus.sidebar_filter_changed.emit(f"search:{keyword}")
        log.debug("Arama: %r — %d sonuc", keyword, len(results))
