from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QStackedWidget,
)

# pyrefly: ignore [missing-import]
import qtawesome as qta
from core.constants.strings import AppStrings
from models.idea import IdeaStatus
from ui.components.idea_card import IdeaCard
from ui.components.idea_form import IdeaForm
from ui.controllers.main_controller import MainController

class KanbanColumn(QFrame):
    def __init__(self, title: str, status: IdeaStatus, parent=None):
        super().__init__(parent)
        self.setObjectName("KanbanColumn")
        self.status = status
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Column Header
        lbl = QLabel(title)
        lbl.setObjectName("KanbanColumnTitle")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        
        # Scroll Area for Cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("KanbanScrollArea")
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.container = QWidget()
        self.container.setObjectName("KanbanContainer")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(8)
        self.container_layout.addStretch()
        
        scroll.setWidget(self.container)
        layout.addWidget(scroll)

    def add_card(self, card: IdeaCard):
        # Insert before the stretch
        self.container_layout.insertWidget(self.container_layout.count() - 1, card)

    def clear(self):
        # Remove all widgets except stretch
        while self.container_layout.count() > 1:
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

class IdeaView(QFrame):
    """Fikirler sayfasinin ana cercevesi (Kanban Panosu + Form Stack)."""

    def __init__(self, controller: MainController, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("IdeaView")
        self._controller = controller
        
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # Header Bar
        header_layout = QHBoxLayout()
        title = QLabel(AppStrings.IDEAS)
        title.setObjectName("ViewTitle")
        
        self._add_btn = QPushButton(AppStrings.ADD_IDEA)
        self._add_btn.setObjectName("PrimaryButton")
        self._add_btn.setIcon(qta.icon("fa5s.plus", color="white"))
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self._add_btn)
        root.addLayout(header_layout)

        # Stack: Kanban vs Form
        self._stack = QStackedWidget()
        
        # 1. Kanban Board
        self._board_widget = QWidget()
        board_layout = QHBoxLayout(self._board_widget)
        board_layout.setContentsMargins(0, 0, 0, 0)
        board_layout.setSpacing(12)
        
        self._cols = {
            IdeaStatus.NEW: KanbanColumn(AppStrings.IDEA_STATUS_NEW, IdeaStatus.NEW),
            IdeaStatus.EVALUATING: KanbanColumn(AppStrings.IDEA_STATUS_EVALUATING, IdeaStatus.EVALUATING),
            IdeaStatus.APPROVED: KanbanColumn(AppStrings.IDEA_STATUS_APPROVED, IdeaStatus.APPROVED),
            IdeaStatus.REJECTED: KanbanColumn(AppStrings.IDEA_STATUS_REJECTED, IdeaStatus.REJECTED),
        }
        
        for col in self._cols.values():
            board_layout.addWidget(col)
            
        self._stack.addWidget(self._board_widget)

        # 2. Form View
        self._form_container = QWidget()
        form_layout = QVBoxLayout(self._form_container)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._form = IdeaForm()
        self._form.setFixedWidth(500)
        form_layout.addWidget(self._form)
        self._stack.addWidget(self._form_container)

        root.addWidget(self._stack)

        # Sinyaller
        self._add_btn.clicked.connect(self._show_form_for_new)
        self._form.cancelled.connect(self._show_board)
        self._form.submitted.connect(self._on_form_submitted)

    def load_all(self):
        """Tum fikirleri veritabanindan cekip sutunlara dagitir."""
        self._show_board()
        for col in self._cols.values():
            col.clear()
            
        ideas = self._controller.load_ideas()
        for idea in ideas:
            card = IdeaCard(idea)
            card.move_left_requested.connect(self._on_move_left)
            card.move_right_requested.connect(self._on_move_right)
            card.delete_requested.connect(self._on_delete_requested)
            card.edit_requested.connect(self._on_edit_requested)
            
            if idea.status in self._cols:
                self._cols[idea.status].add_card(card)

    def _show_board(self):
        self._stack.setCurrentIndex(0)
        self._add_btn.setVisible(True)

    def _show_form_for_new(self):
        self._form.clear()
        self._stack.setCurrentIndex(1)
        self._add_btn.setVisible(False)

    def _on_edit_requested(self, idea_id: int):
        idea = self._controller.get_idea(idea_id)
        if idea:
            self._form.load_idea(idea)
            self._stack.setCurrentIndex(1)
            self._add_btn.setVisible(False)

    def _on_form_submitted(self, data: dict):
        idea_id = data.pop("idea_id", None)
        if idea_id is None:
            self._controller.add_idea(data)
        else:
            self._controller.update_idea(idea_id, data)
            
        # UI otomatik guncellenecek (EventBus -> ContentWorkspace.refresh -> IdeaView.load_all)
        # Ama IdeaView icinde oldugumuz icin EventBus tetiklendi, load_all cagrilacak.

    def _on_delete_requested(self, idea_id: int):
        reply = QMessageBox.question(
            self,
            "Onay",
            "Bu fikri kalıcı olarak silmek istiyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._controller.delete_idea(idea_id)

    def _on_move_left(self, idea_id: int):
        idea = self._controller.get_idea(idea_id)
        if not idea: return
        
        flow = [IdeaStatus.NEW, IdeaStatus.EVALUATING, IdeaStatus.APPROVED]
        if idea.status == IdeaStatus.REJECTED:
            # Reddedileni geri degerlendirmeye al
            new_status = IdeaStatus.EVALUATING
        else:
            idx = flow.index(idea.status)
            if idx > 0:
                new_status = flow[idx - 1]
            else:
                return
                
        self._controller.update_idea(idea_id, {"status": new_status})

    def _on_move_right(self, idea_id: int):
        idea = self._controller.get_idea(idea_id)
        if not idea: return
        
        flow = [IdeaStatus.NEW, IdeaStatus.EVALUATING, IdeaStatus.APPROVED]
        if idea.status in flow:
            idx = flow.index(idea.status)
            if idx < len(flow) - 1:
                new_status = flow[idx + 1]
            else:
                return
            self._controller.update_idea(idea_id, {"status": new_status})
