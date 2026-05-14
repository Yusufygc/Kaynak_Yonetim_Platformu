from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from core.constants.strings import AppStrings


class CategoryRow(QFrame):
    """Tek kategori satiri: isim + renk onizleme + duzenle/sil kontrolleri."""

    edit_requested = Signal(int, str, str, str)   # (id, name, color_hex, icon)
    delete_requested = Signal(int)                 # id

    def __init__(self, category, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("CategoryRow")
        self._cat_id: int = category.id
        self._cat_icon: str = category.icon or ""
        self._confirm_pending: bool = False

        self._build_ui(category)

    def _build_ui(self, category) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(8)

        # Renk kutusu
        self._color_box = QLabel()
        self._color_box.setObjectName("ColorPreviewBox")
        self._color_box.setFixedSize(18, 18)
        self._set_color(category.color_hex or "#888888")
        layout.addWidget(self._color_box)

        # Isim — normal gosterim
        self._name_label = QLabel(category.name)
        self._name_label.setObjectName("CategoryRowLabel")
        layout.addWidget(self._name_label, stretch=1)

        # Inline duzenle alanlari (gizli)
        self._name_edit = QLineEdit(category.name)
        self._name_edit.setObjectName("RowEditField")
        self._name_edit.hide()
        layout.addWidget(self._name_edit, stretch=1)

        self._color_edit = QLineEdit(category.color_hex or "")
        self._color_edit.setObjectName("RowEditField")
        self._color_edit.setFixedWidth(90)
        self._color_edit.setPlaceholderText("#RRGGBB")
        self._color_edit.hide()
        layout.addWidget(self._color_edit)

        # Butonlar
        self._edit_btn = QPushButton(AppStrings.EDIT)
        self._edit_btn.setObjectName("RowEditButton")
        self._edit_btn.setFixedWidth(70)
        layout.addWidget(self._edit_btn)

        self._save_btn = QPushButton(AppStrings.SAVE)
        self._save_btn.setObjectName("RowSaveButton")
        self._save_btn.setFixedWidth(70)
        self._save_btn.hide()
        layout.addWidget(self._save_btn)

        self._cancel_edit_btn = QPushButton(AppStrings.CANCEL)
        self._cancel_edit_btn.setObjectName("RowCancelButton")
        self._cancel_edit_btn.setFixedWidth(70)
        self._cancel_edit_btn.hide()
        layout.addWidget(self._cancel_edit_btn)

        self._delete_btn = QPushButton(AppStrings.DELETE)
        self._delete_btn.setObjectName("RowDeleteButton")
        self._delete_btn.setFixedWidth(80)
        layout.addWidget(self._delete_btn)

        self._edit_btn.clicked.connect(self._enter_edit_mode)
        self._save_btn.clicked.connect(self._on_save)
        self._cancel_edit_btn.clicked.connect(self._exit_edit_mode)
        self._delete_btn.clicked.connect(self._on_delete_click)

    # ------------------------------------------------------------------ #

    def _set_color(self, hex_str: str) -> None:
        try:
            color = QColor(hex_str)
            bg = hex_str if color.isValid() else "#888888"
        except Exception:
            bg = "#888888"
        self._color_box.setStyleSheet(
            f"background-color: {bg}; border-radius: 3px; border: 1px solid #555;"
        )

    def _enter_edit_mode(self) -> None:
        self._name_label.hide()
        self._name_edit.show()
        self._color_edit.show()
        self._edit_btn.hide()
        self._save_btn.show()
        self._cancel_edit_btn.show()
        self._delete_btn.hide()
        self._confirm_pending = False

    def _exit_edit_mode(self) -> None:
        self._name_edit.hide()
        self._color_edit.hide()
        self._save_btn.hide()
        self._cancel_edit_btn.hide()
        self._name_label.show()
        self._edit_btn.show()
        self._delete_btn.show()

    def _on_save(self) -> None:
        name = self._name_edit.text().strip()
        color = self._color_edit.text().strip()
        if not name or not color:
            return
        self.edit_requested.emit(self._cat_id, name, color, self._cat_icon)
        self._name_label.setText(name)
        self._set_color(color)
        self._exit_edit_mode()

    def _on_delete_click(self) -> None:
        if not self._confirm_pending:
            self._delete_btn.setText(AppStrings.CONFIRM_DELETE)
            self._delete_btn.setObjectName("RowDeleteConfirmButton")
            self._delete_btn.style().unpolish(self._delete_btn)
            self._delete_btn.style().polish(self._delete_btn)
            self._confirm_pending = True
        else:
            self.delete_requested.emit(self._cat_id)

    def refresh(self, category) -> None:
        self._name_label.setText(category.name)
        self._name_edit.setText(category.name)
        self._color_edit.setText(category.color_hex or "")
        self._set_color(category.color_hex or "#888888")
        self._cat_icon = category.icon or ""
