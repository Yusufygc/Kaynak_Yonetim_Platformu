from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QApplication

from pkm_app.ui.controllers import resource_flow as resource_flow_module
from pkm_app.ui.controllers.main_controller import MainController
from pkm_app.ui.controllers.resource_flow import ResourceFlow


def _pump_events(times: int = 20) -> None:
    for _ in range(times):
        QApplication.processEvents()


def test_schedule_scrape_updates_resource_metadata_in_background(qapp, session, monkeypatch):
    # Modul-yolu string'i degil, dogrudan sinif referansi uzerinden patch:
    # pkm_app paketinin bare/qualified import aliasing'i, string tabanli
    # monkeypatch.setattr("a.b.c...") cozumlemesini guvenilmez kilabiliyor.
    monkeypatch.setattr(
        resource_flow_module.ScraperService, "extract_metadata", lambda self, url: {"og_title": "Baslik"}
    )

    controller = MainController(session)
    resource = controller.add_resource({"title": "Kaynak", "url": "https://example.com"})
    assert resource is not None
    assert resource.extra_metadata is None  # ekleme aninda senkron scrape yapilmadi

    flow = ResourceFlow(controller, workspace=None, detail_view=None)
    flow._schedule_scrape(resource)

    assert QThreadPool.globalInstance().waitForDone(2000)
    _pump_events()

    updated = controller.get_resource(resource.id)
    assert updated.extra_metadata == {"og_title": "Baslik"}


def test_schedule_scrape_skips_when_no_url(qapp, session):
    controller = MainController(session)
    resource = controller.add_resource({"title": "URL'siz kaynak"})
    assert resource is not None

    flow = ResourceFlow(controller, workspace=None, detail_view=None)
    flow._schedule_scrape(resource)

    assert QThreadPool.globalInstance().waitForDone(500)
    _pump_events()

    assert controller.get_resource(resource.id).extra_metadata is None


def test_on_scrape_finished_ignores_empty_metadata(qapp, session):
    controller = MainController(session)
    resource = controller.add_resource({"title": "Kaynak", "url": "https://example.com"})
    assert resource is not None

    flow = ResourceFlow(controller, workspace=None, detail_view=None)
    flow._on_scrape_finished(resource.id, {})

    assert controller.get_resource(resource.id).extra_metadata is None
