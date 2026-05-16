from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# pyrefly: ignore [missing-import]
import qtawesome as qta
from models.idea import Idea, IdeaStatus
from ui.components.painted import AccentFrame

class IdeaCard(AccentFrame):
    """Kanban panosunda fikirleri gosteren kart."""

    move_left_requested = Signal(int)
    move_right_requested = Signal(int)
    delete_requested = Signal(int)
    edit_requested = Signal(int)

    def __init__(self, idea: Idea, parent: QWidget | None = None) -> None:
        # Öncelik rengini belirle (accent_color icin)
        # 1: High (Kırmızımsı), 2: Medium (Sarımsı/Mavi), 3: Low (Gri/Yesil)
        accent_color = "#94a3b8"  # Default gray
        if idea.priority == 1:
            accent_color = "#ef4444"  # Red
        elif idea.priority == 2:
            accent_color = "#3b82f6"  # Blue
            
        super().__init__(parent=parent)
        self.set_accent_color(accent_color)
        self.setObjectName("IdeaCard")
        self._idea = idea
        self.setMinimumHeight(100)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        # Ust satir: Baslik ve Priority
        top_layout = QHBoxLayout()
        title_lbl = QLabel(self._idea.title)
        title_lbl.setObjectName("IdeaCardTitle")
        title_lbl.setWordWrap(True)
        # Baslik fontunu ResourceCard ile uyumlu yapalim (QSS ile yapilabilir)
        
        pri_str = "Yüksek" if self._idea.priority == 1 else "Orta" if self._idea.priority == 2 else "Düşük"
        pri_lbl = QLabel(pri_str)
        pri_lbl.setObjectName("IdeaPriorityBadge")
        
        top_layout.addWidget(title_lbl, stretch=1)
        top_layout.addWidget(pri_lbl)
        layout.addLayout(top_layout)

        # Aciklama (Eger varsa)
        if self._idea.description:
            desc_lbl = QLabel(self._idea.description)
            desc_lbl.setWordWrap(True)
            desc_lbl.setObjectName("IdeaCardDesc")
            layout.addWidget(desc_lbl)

        layout.addStretch()

        # Alt satir: Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(4)
        
        # Sola tasi (Geri)
        self._left_btn = QPushButton()
        self._left_btn.setIcon(qta.icon("fa5s.chevron-left"))
        self._left_btn.setToolTip("Bir önceki aşamaya taşı")
        self._left_btn.setFixedSize(24, 24)
        self._left_btn.setObjectName("IconButton")
        if self._idea.status == IdeaStatus.NEW:
            self._left_btn.setEnabled(False)
            
        # Saga tasi (Ileri)
        self._right_btn = QPushButton()
        self._right_btn.setIcon(qta.icon("fa5s.chevron-right"))
        self._right_btn.setToolTip("Bir sonraki aşamaya taşı")
        self._right_btn.setFixedSize(24, 24)
        self._right_btn.setObjectName("IconButton")
        if self._idea.status == IdeaStatus.REJECTED or self._idea.status == IdeaStatus.APPROVED:
            self._right_btn.setEnabled(False)

        # Düzenle
        self._edit_btn = QPushButton()
        self._edit_btn.setIcon(qta.icon("fa5s.pen"))
        self._edit_btn.setToolTip("Düzenle")
        self._edit_btn.setFixedSize(24, 24)
        self._edit_btn.setObjectName("IconButton")

        # Sil
        self._delete_btn = QPushButton()
        self._delete_btn.setIcon(qta.icon("fa5s.trash-alt", color="#ef4444"))
        self._delete_btn.setToolTip("Sil")
        self._delete_btn.setFixedSize(24, 24)
        self._delete_btn.setObjectName("IconButton")

        btn_layout.addWidget(self._left_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self._edit_btn)
        btn_layout.addWidget(self._delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self._right_btn)

        layout.addLayout(btn_layout)

        # Connect
        self._left_btn.clicked.connect(lambda: self.move_left_requested.emit(self._idea.id))
        self._right_btn.clicked.connect(lambda: self.move_right_requested.emit(self._idea.id))
        self._delete_btn.clicked.connect(lambda: self.delete_requested.emit(self._idea.id))
        self._edit_btn.clicked.connect(lambda: self.edit_requested.emit(self._idea.id))
