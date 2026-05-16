from core.events import event_bus
from core.logger import log
from ui.controllers.main_controller import MainController
from ui.views.content_workspace import ContentWorkspace
from ui.views.detail_view import DetailView


class ResourceFlow:
    """UI bilesenleri ve MainController arasindaki kaynak yasam dongusu koordinatoru.

    MainWindow ince compose'a indi; sinyal kablolama ve flow handler'lari burada.
    UI widget degildir, sadece sinyal yonlendirir.
    """

    def __init__(
        self,
        controller: MainController,
        workspace: ContentWorkspace,
        detail_view: DetailView,
    ) -> None:
        self._controller = controller
        self._workspace = workspace
        self._detail = detail_view

    def wire(self) -> None:
        # Event Bus → workspace / detail
        event_bus.sidebar_filter_changed.connect(self._on_filter_changed)
        event_bus.resource_selected.connect(self._on_resource_selected)
        event_bus.resource_added.connect(self._on_resource_changed)
        event_bus.resource_updated.connect(self._on_resource_changed)
        event_bus.resource_deleted.connect(self._on_resource_deleted)
        event_bus.error_occurred.connect(self._workspace.show_error_banner)

        # Pin / Favori toggle
        event_bus.resource_pin_toggle_requested.connect(self._controller.toggle_pin)
        event_bus.resource_favorite_toggle_requested.connect(
            self._controller.toggle_favorite
        )

        # Workspace → flow
        self._workspace.add_requested.connect(self._on_add_requested)

        # Detail panel → flow / controller
        self._detail.progress_updated.connect(self._controller.update_progress)
        self._detail.status_updated.connect(self._on_status_updated)
        self._detail.content_updated.connect(self._on_content_updated)
        self._detail.form_submitted.connect(self._on_form_submitted)
        self._detail.edit_requested.connect(self._on_edit_requested)
        self._detail.delete_requested.connect(self._on_delete_requested)

    # ------------------------------------------------------------------ #
    # Event Bus handler'lari
    # ------------------------------------------------------------------ #

    def _on_filter_changed(self, filter_key: str) -> None:
        if filter_key == "settings" or filter_key == "url_showcase":
            self._detail.clear()
        self._workspace.apply_filter(filter_key)

    def _on_resource_selected(self, resource_id: int) -> None:
        resource = self._controller.get_resource(resource_id)
        if resource:
            self._detail.load_resource(resource)

    def _on_resource_changed(self, _resource_id: int = 0) -> None:
        self._workspace.refresh()
        current_detail_id = self._detail.current_resource_id()
        if current_detail_id is not None:
            resource = self._controller.get_resource(current_detail_id)
            if resource is not None:
                self._detail.load_resource(resource)

    def _on_resource_deleted(self, _resource_id: int = 0) -> None:
        if self._workspace.is_content_active():
            self._workspace.refresh()

    # ------------------------------------------------------------------ #
    # UI sinyal handler'lari
    # ------------------------------------------------------------------ #

    def _on_add_requested(self) -> None:
        categories = self._controller.load_categories()
        self._detail.show_form(categories)

    def _on_edit_requested(self, resource_id: int) -> None:
        resource = self._controller.get_resource(resource_id)
        categories = self._controller.load_categories()
        if resource:
            self._detail.show_form_edit(resource, categories)

    def _on_delete_requested(self, resource_id: int) -> None:
        self._controller.delete_resource(resource_id)
        self._detail.clear()

    def _on_status_updated(self, resource_id: int, status) -> None:
        self._controller.update_resource(resource_id, {"status": status})

    def _on_content_updated(self, resource_id: int, text: str) -> None:
        self._controller.update_resource(resource_id, {"content": text or None})
        self._workspace.show_info_banner("Not kaydedildi.")

    def _on_form_submitted(self, data: dict) -> None:
        resource_id = data.pop("resource_id", None)
        if resource_id is None:
            resource = self._controller.add_resource(data)
            if resource is not None:
                self._detail.clear()
                self._workspace.refresh()
                self._workspace.show_info_banner(f"'{resource.title}' eklendi.")
                log.info("Form ile kaynak eklendi: id=%d", resource.id)
        else:
            resource = self._controller.update_resource(resource_id, data)
            if resource is not None:
                self._detail.load_resource(resource)
                self._workspace.refresh()
                self._workspace.show_info_banner(f"'{resource.title}' guncellendi.")
                log.info("Form ile kaynak guncellendi: id=%d", resource.id)
