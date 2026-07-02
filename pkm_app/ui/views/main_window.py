from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QSplitter, QWidget, QGraphicsOpacityEffect

from core.constants.strings import AppStrings
from core.events import event_bus
from ui.components.sidebar import Sidebar
from ui.controllers.resource_flow import ResourceFlow
from ui.views.content_workspace import ContentWorkspace
from ui.views.detail_view import DetailView


class MainWindow(QMainWindow):
    """Ince compose: Sidebar | ContentWorkspace | DetailView.

    Tum kaynak yasam dongusu kablolama ResourceFlow icinde; filter dispatch
    ContentWorkspace icinde. Buradaki dosya sadece pencere iskeletini kurar.
    """

    def __init__(self, controller) -> None:
        super().__init__()
        self.setWindowTitle(AppStrings.APP_TITLE)
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)

        self._sidebar = Sidebar()
        self._workspace = ContentWorkspace(controller)
        self._detail_view = DetailView()

        self._build_ui()

        self._flow = ResourceFlow(controller, self._workspace, self._detail_view)
        self._flow.wire()

        self._sidebar.select_by_key("url_showcase")
        self._workspace.apply_filter("url_showcase")

        # Tema degisiminde yumusak gecis saglayan fade-in animasyonu
        event_bus.theme_changed.connect(self._on_theme_changed_fade)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._sidebar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("MainSplitter")
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self._workspace)
        splitter.addWidget(self._detail_view)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        root_layout.addWidget(splitter, stretch=1)

    def _on_theme_changed_fade(self, theme_data: dict) -> None:
        central = self.centralWidget()
        if not central:
            return
            
        self._opacity_effect = QGraphicsOpacityEffect(central)
        central.setGraphicsEffect(self._opacity_effect)
        
        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_anim.setDuration(250)  # 250ms yumusak gecis suresi
        self._fade_anim.setStartValue(0.65)  # Solukluk baslangici
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Animasyon bitince performans acisindan efekti temizle
        self._fade_anim.finished.connect(lambda: central.setGraphicsEffect(None))
        self._fade_anim.start()

