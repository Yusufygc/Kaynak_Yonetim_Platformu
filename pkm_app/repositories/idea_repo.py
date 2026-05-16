from typing import List
from models.idea import Idea, IdeaStatus
from .base_repository import BaseRepository
from sqlalchemy.orm import Session

class IdeaRepository(BaseRepository[Idea]):
    def __init__(self, session: Session) -> None:
        super().__init__(Idea, session)

    def get_by_status(self, status: IdeaStatus) -> List[Idea]:
        return self._session.query(Idea).filter(Idea.status == status).order_by(Idea.priority.asc(), Idea.created_at.desc()).all()

    def get_all_ordered(self) -> List[Idea]:
        return self._session.query(Idea).order_by(Idea.priority.asc(), Idea.created_at.desc()).all()
