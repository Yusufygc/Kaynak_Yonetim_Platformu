from typing import List, Optional
from models.idea import Idea, IdeaStatus
from repositories.idea_repo import IdeaRepository
from sqlalchemy.orm import Session
from core.events import event_bus
from core.exceptions import ValidationError
from core.logger import log
from .schemas import IdeaUpdateSchema

class IdeaService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repo = IdeaRepository(session)

    def get_all_ideas(self) -> List[Idea]:
        return self._repo.get_all_ordered()

    def get_idea(self, idea_id: int) -> Optional[Idea]:
        return self._repo.get_by_id(idea_id)

    def create_idea(self, title: str, description: str = "", status: IdeaStatus = IdeaStatus.NEW, priority: int = 2) -> Idea:
        if not title or not title.strip():
            raise ValidationError("Fikir başlığı boş olamaz.")
        
        idea = Idea(
            title=title.strip(),
            description=description.strip() if description else "",
            status=status,
            priority=priority
        )
        try:
            self._repo.create(idea)
            self._session.commit()
            event_bus.idea_added.emit(idea.id)
            return idea
        except Exception:
            self._session.rollback()
            log.exception("Fikir kaydedilirken hata olustu.")
            raise

    def update_idea(self, idea_id: int, payload: IdeaUpdateSchema) -> Idea:
        idea = self._repo.get_by_id(idea_id)
        if not idea:
            raise ValidationError("Güncellenecek fikir bulunamadı.")

        fields = payload.model_fields_set

        if "title" in fields:
            title = payload.title
            if not title or not title.strip():
                raise ValidationError("Fikir başlığı boş olamaz.")
            idea.title = title.strip()

        if "description" in fields:
            idea.description = (payload.description or "").strip()

        if "status" in fields:
            idea.status = payload.status

        if "priority" in fields:
            idea.priority = payload.priority


        try:
            self._session.commit()
            event_bus.idea_updated.emit(idea.id)
            return idea
        except Exception:
            self._session.rollback()
            log.exception("Fikir guncellenirken hata olustu.")
            raise

    def delete_idea(self, idea_id: int) -> None:
        idea = self._repo.get_by_id(idea_id)
        if not idea:
            raise ValidationError("Silinecek fikir bulunamadı.")
            
        try:
            self._repo.delete(idea.id)
            self._session.commit()
            event_bus.idea_deleted.emit(idea_id)
        except Exception:
            self._session.rollback()
            log.exception("Fikir silinirken hata olustu.")
            raise
