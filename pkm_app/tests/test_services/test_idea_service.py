# pyrefly: ignore [missing-import]
import pytest
from pkm_app.models.idea import Idea, IdeaStatus
from pkm_app.services.idea_service import IdeaService
from pkm_app.core.exceptions import ValidationError

def test_create_idea_success(session):
    svc = IdeaService(session)
    idea = svc.create_idea("Yeni Uygulama Fikri", "Test aciklamasi", IdeaStatus.NEW, 1)
    
    assert idea.id is not None
    assert idea.title == "Yeni Uygulama Fikri"
    assert idea.description == "Test aciklamasi"
    assert idea.status == IdeaStatus.NEW
    assert idea.priority == 1

def test_create_idea_empty_title(session):
    svc = IdeaService(session)
    with pytest.raises(ValidationError):
        svc.create_idea("")

def test_update_idea(session):
    svc = IdeaService(session)
    idea = svc.create_idea("Fikir 1")
    
    updated = svc.update_idea(idea.id, {"title": "Guncel Fikir 1", "status": IdeaStatus.EVALUATING})
    assert updated.title == "Guncel Fikir 1"
    assert updated.status == IdeaStatus.EVALUATING

def test_delete_idea(session):
    svc = IdeaService(session)
    idea = svc.create_idea("Silinecek")
    svc.delete_idea(idea.id)
    
    assert svc.get_idea(idea.id) is None

def test_get_all_ordered(session):
    svc = IdeaService(session)
    svc.create_idea("C", priority=3)
    svc.create_idea("A", priority=1)
    svc.create_idea("B", priority=2)
    
    ideas = svc.get_all_ideas()
    assert len(ideas) == 3
    assert ideas[0].title == "A"
    assert ideas[1].title == "B"
    assert ideas[2].title == "C"
