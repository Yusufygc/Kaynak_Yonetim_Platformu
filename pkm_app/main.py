import sys
from pathlib import Path

# pkm_app/ dizinini Python yoluna ekle
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtWidgets import QApplication

from core.config import settings
from core.logger import log
from core.theme_manager import theme_manager
from ui.controllers.main_controller import MainController
from ui.views.main_window import MainWindow
from utils.db_utils import get_session, init_db


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("PKM")

    log.info("Uygulama baslatiliyor...")

    init_db()

    session = get_session()
    controller = MainController(session)

    theme_manager.apply_theme(settings.DEFAULT_THEME)

    window = MainWindow(controller)
    window.show()

    exit_code = app.exec()
    session.close()
    log.info("Uygulama kapatildi.")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
