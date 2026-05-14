from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from core.constants.strings import AppStrings


class TagRow(QFrame):
    """Tek etiket satiri: isim + duzenle/sil kontrolleri."""

    edit_requested = Signal(int, str)   # (id, new_name)
    delete_requested = Signal(int)      # id

    def __init__(self, tag, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("TagRow")
        self._tag_id: int = tag.id
        self._confirm_pending: bool = False
        self._build_ui(tag)

    def _build_ui(self, tag) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(8)

        self._name_label = QLabel(f"#{tag.name}")
        self._name_label.setObjectName("TagRowLabel")
        layout.addWidget(self._name_label, stretch=1)

        self._name_edit = QLineEdit(tag.name)
        self._name_edit.setObjectName("RowEditField")
        self._name_edit.hide()
        layout.addWidget(self._name_edit, stretch=1)

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

    def _enter_edit_mode(self) -> None:
        self._name_label.hide()
        self._name_edit.show()
        self._edit_btn.hide()
        self._save_btn.show()
        self._cancel_edit_btn.show()
        self._delete_btn.hide()
        self._confirm_pending = False

    def _exit_edit_mode(self) -> None:
        self._name_edit.hide()
        self._save_btn.hide()
        self._cancel_edit_btn.hide()
        self._name_label.show()
        self._edit_btn.show()
        self._delete_btn.show()

    def _on_save(self) -> None:
        new_name = self._name_edit.text().strip()
        if not new_name:
            return
        self.edit_requested.emit(self._tag_id, new_name)
        self._name_label.setText(f"#{new_name}")
        self._exit_edit_mode()

    def _on_delete_click(self) -> None:
        if not self._confirm_pending:
            self._delete_btn.setText(AppStrings.CONFIRM_DELETE)
            self._delete_btn.setObjectName("RowDeleteConfirmButton")
            self._delete_btn.style().unpolish(self._delete_btn)
            self._delete_btn.style().polish(self._delete_btn)
            self._confirm_pending = True
        else:
            self.delete_requested.emit(self._tag_id)
