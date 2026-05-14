from sqlalchemy.orm import Session

from core.events import event_bus
from core.logger import log
from models.resource import Resource, ResourceStatus
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
        if filter_key == "inbox":
            return self._resource_svc.get_by_status(ResourceStatus.INBOX)
        if filter_key == "planned":
            return self._resource_svc.get_by_status(ResourceStatus.PLANNED)
        if filter_key == "url_showcase":
            return self._resource_svc.get_urls_only()
        if filter_key.startswith("category:"):
            cat_id = int(filter_key.split(":")[1])
            return self._resource_svc.get_by_category(cat_id)
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

    def search_resources(self, keyword: str) -> list[Resource]:
        if not keyword.strip():
            return self._resource_svc.get_all()
        return self._resource_svc.search(keyword)

    def update_resource(self, resource_id: int, data: dict) -> Resource | None:
        try:
            resource = self._resource_svc.update_resource(resource_id, data)
            event_bus.resource_updated.emit(resource_id)
            return resource
        except Exception as exc:
            log.error("[%s] Kaynak guncellenemedi: %s", exc.__class__.__name__, exc)
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

    def create_category(self, name: str, color_hex: str, icon: str = "") -> object:
        try:
            cat = self._category_svc.create_category(name, color_hex, icon)
            event_bus.category_added.emit(cat.id)
            return cat
        except Exception as exc:
            log.error("Kategori eklenemedi: %s", exc)
            event_bus.error_occurred.emit(str(exc))
            return None

    def update_category(self, category_id: int, name: str,
                        color_hex: str, icon: str = "") -> object:
        try:
            cat = self._category_svc.update_category(category_id, name, color_hex, icon)
            event_bus.category_updated.emit(cat.id)
            return cat
        except Exception as exc:
            log.error("Kategori guncellenemedi: %s", exc)
            event_bus.error_occurred.emit(str(exc))
            return None

    def delete_category(self, category_id: int) -> bool:
        try:
            self._category_svc.delete_category(category_id)
            event_bus.category_deleted.emit(category_id)
            return True
        except Exception as exc:
            log.error("Kategori silinemedi: %s", exc)
            event_bus.error_occurred.emit(str(exc))
            return False

    def create_tag(self, name: str) -> object:
        try:
            tag = self._tag_svc.create_tag(name)
            event_bus.tag_added.emit(tag.id)
            return tag
        except Exception as exc:
            log.error("Etiket eklenemedi: %s", exc)
            event_bus.error_occurred.emit(str(exc))
            return None

    def update_tag(self, tag_id: int, new_name: str) -> object:
        try:
            tag = self._tag_svc.update_tag(tag_id, new_name)
            event_bus.tag_updated.emit(tag.id)
            return tag
        except Exception as exc:
            log.error("Etiket guncellenemedi: %s", exc)
            event_bus.error_occurred.emit(str(exc))
            return None

    def delete_tag(self, tag_id: int) -> bool:
        try:
            self._tag_svc.delete_tag(tag_id)
            event_bus.tag_deleted.emit(tag_id)
            return True
        except Exception as exc:
            log.error("Etiket silinemedi: %s", exc)
            event_bus.error_occurred.emit(str(exc))
            return False

    # ------------------------------------------------------------------ #
    # Slot'lar
    # ------------------------------------------------------------------ #

    def _on_search(self, keyword: str) -> None:
        event_bus.sidebar_filter_changed.emit(f"search:{keyword}")
