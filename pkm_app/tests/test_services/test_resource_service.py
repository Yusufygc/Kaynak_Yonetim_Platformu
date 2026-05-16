import pytest

from pkm_app.core.exceptions import InvalidURLError, ValidationError
from pkm_app.models import Resource, ResourceStatus
from pkm_app.services.category_service import CategoryService
from pkm_app.services.resource_service import ResourceService


def test_deleting_category_keeps_resource_and_clears_category(session):
    category = CategoryService(session).create_category("Python", "#3776AB")
    resource = ResourceService(session).add_new_resource(
        {
            "title": "Docs",
            "category_id": category.id,
            "extra_metadata": {},
        }
    )

    CategoryService(session).delete_category(category.id)
    session.expire_all()

    persisted = session.get(Resource, resource.id)
    assert persisted is not None
    assert persisted.category_id is None


def test_add_resource_deduplicates_tag_names(session):
    resource = ResourceService(session).add_new_resource(
        {
            "title": "Tags",
            "tag_names": ["Python", " python ", "SQL"],
        }
    )

    assert [tag.name for tag in resource.tags] == ["python", "sql"]


def test_update_resource_replaces_tag_names(session):
    service = ResourceService(session)
    resource = service.add_new_resource(
        {
            "title": "Tags",
            "tag_names": ["old"],
        }
    )

    updated = service.update_resource(resource.id, {"tag_names": ["new", "NEW"]})

    assert [tag.name for tag in updated.tags] == ["new"]


def test_update_resource_with_empty_tag_list_clears_tags(session):
    service = ResourceService(session)
    resource = service.add_new_resource(
        {
            "title": "Tags",
            "tag_names": ["old"],
        }
    )

    updated = service.update_resource(resource.id, {"tag_names": []})

    assert updated.tags == []


def test_add_resource_merges_url_tag_with_manual_tags(session, monkeypatch):
    monkeypatch.setattr(
        "pkm_app.services.resource_service.ScraperService.extract_metadata",
        lambda self, url: {},
    )

    resource = ResourceService(session).add_new_resource(
        {
            "title": "Video",
            "url": "https://youtu.be/abc123",
            "tag_names": ["AI", "youtube"],
        }
    )

    assert [tag.name for tag in resource.tags] == ["ai", "youtube"]


@pytest.mark.parametrize(
    ("url", "expected_tag"),
    [
        ("https://www.linkedin.com/posts/example", "linkedin"),
        ("https://instagram.com/reel/abc", "instagram"),
        ("https://github.com/example/repo", "github"),
        ("https://docs.python.org/3/", "python"),
    ],
)
def test_add_resource_derives_tags_from_url(session, monkeypatch, url, expected_tag):
    monkeypatch.setattr(
        "pkm_app.services.resource_service.ScraperService.extract_metadata",
        lambda self, url: {},
    )

    resource = ResourceService(session).add_new_resource(
        {
            "title": "URL",
            "url": url,
        }
    )

    assert [tag.name for tag in resource.tags] == [expected_tag]


def test_update_url_adds_new_url_tag_and_preserves_existing_tags(session, monkeypatch):
    monkeypatch.setattr(
        "pkm_app.services.resource_service.ScraperService.extract_metadata",
        lambda self, url: {},
    )
    service = ResourceService(session)
    resource = service.add_new_resource(
        {
            "title": "URL",
            "url": "https://github.com/example/repo",
            "tag_names": ["manual"],
        }
    )

    updated = service.update_resource(
        resource.id,
        {"url": "https://www.linkedin.com/posts/example"},
    )

    assert [tag.name for tag in updated.tags] == ["manual", "github", "linkedin"]


@pytest.mark.parametrize(
    ("progress", "expected_status"),
    [
        (0, ResourceStatus.PLANNED),
        (25, ResourceStatus.IN_PROGRESS),
        (100, ResourceStatus.COMPLETED),
    ],
)
def test_progress_updates_status(session, progress, expected_status):
    service = ResourceService(session)
    resource = service.add_new_resource({"title": "Progress"})

    updated = service.update_resource_progress(resource.id, progress)

    assert updated.progress == progress
    assert updated.status == expected_status


@pytest.mark.parametrize(
    ("status", "expected_progress"),
    [
        (ResourceStatus.INBOX, 0),
        (ResourceStatus.PLANNED, 0),
        (ResourceStatus.IN_PROGRESS, 25),
        (ResourceStatus.COMPLETED, 100),
    ],
)
def test_status_updates_progress(session, status, expected_progress):
    service = ResourceService(session)
    resource = service.add_new_resource({"title": "Status"})

    updated = service.update_resource(resource.id, {"status": status})

    assert updated.status == status
    assert updated.progress == expected_progress


@pytest.mark.parametrize(
    ("data", "expected_error"),
    [
        ({"title": "Bad URL", "url": "ftp://example.com"}, InvalidURLError),
        ({"title": "Bad Priority", "priority": 9}, ValidationError),
    ],
)
def test_validation_errors_leave_session_usable(session, data, expected_error):
    service = ResourceService(session)

    with pytest.raises(expected_error):
        service.add_new_resource(data)

    resource = service.add_new_resource({"title": "Valid"})
    assert resource.id is not None


def test_toggle_pin_flips_value(session):
    service = ResourceService(session)
    resource = service.add_new_resource({"title": "Pin Me"})
    assert resource.is_pinned is False

    service.toggle_pin(resource.id)
    session.expire_all()
    assert session.get(Resource, resource.id).is_pinned is True

    service.toggle_pin(resource.id)
    session.expire_all()
    assert session.get(Resource, resource.id).is_pinned is False


def test_toggle_favorite_flips_value(session):
    service = ResourceService(session)
    resource = service.add_new_resource({"title": "Star Me"})
    assert resource.is_favorite is False

    service.toggle_favorite(resource.id)
    session.expire_all()
    assert session.get(Resource, resource.id).is_favorite is True


def test_query_resources_combines_filters(session):
    service = ResourceService(session)
    r1 = service.add_new_resource(
        {"title": "Hi", "status": ResourceStatus.INBOX, "priority": 1}
    )
    service.add_new_resource(
        {"title": "Lo", "status": ResourceStatus.PLANNED, "priority": 3}
    )
    service.toggle_favorite(r1.id)

    results = service.query_resources(
        {"statuses": [ResourceStatus.INBOX], "priorities": [1]}
    )
    assert [r.id for r in results] == [r1.id]

    favs = service.query_resources({"favorites_only": True})
    assert [r.id for r in favs] == [r1.id]


def test_query_resources_orders_pinned_first(session):
    service = ResourceService(session)
    old = service.add_new_resource({"title": "Old"})
    new = service.add_new_resource({"title": "New"})

    service.toggle_pin(old.id)

    results = service.query_resources({})
    assert results[0].id == old.id  # pinned > created_at
    assert results[1].id == new.id
