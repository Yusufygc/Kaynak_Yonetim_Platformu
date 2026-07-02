from pkm_app.models.idea import Idea, IdeaStatus
from pkm_app.repositories.idea_repo import IdeaRepository


def test_get_all_ordered_by_priority_then_recency(session):
    repo = IdeaRepository(session)
    repo.create(Idea(title="Low", priority=3))
    repo.create(Idea(title="High", priority=1))
    repo.create(Idea(title="Medium", priority=2))

    ideas = repo.get_all_ordered()

    assert [i.title for i in ideas] == ["High", "Medium", "Low"]


def test_get_by_status_filters(session):
    repo = IdeaRepository(session)
    repo.create(Idea(title="New idea", status=IdeaStatus.NEW))
    repo.create(Idea(title="Approved idea", status=IdeaStatus.APPROVED))

    approved = repo.get_by_status(IdeaStatus.APPROVED)

    assert [i.title for i in approved] == ["Approved idea"]
