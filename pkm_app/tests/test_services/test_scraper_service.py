import requests

from pkm_app.services.scraper_service import ScraperService


class _Response:
    def __init__(self, text: str, url: str = "https://example.com/page") -> None:
        self.text = text
        self.url = url

    def raise_for_status(self) -> None:
        return None


def test_extract_metadata_from_open_graph_html(monkeypatch):
    html = """
    <html>
      <head>
        <meta property="og:title" content="OG Title">
        <meta property="og:description" content="OG Description">
        <meta property="og:image" content="/image.png">
        <link rel="shortcut icon" href="/favicon.ico">
      </head>
    </html>
    """

    monkeypatch.setattr(
        "pkm_app.services.scraper_service.requests.get",
        lambda *args, **kwargs: _Response(html),
    )

    metadata = ScraperService().extract_metadata("https://example.com/page")

    assert metadata == {
        "og_title": "OG Title",
        "og_description": "OG Description",
        "thumbnail": "https://example.com/image.png",
        "favicon": "https://example.com/favicon.ico",
    }


def test_extract_metadata_uses_twitter_card_and_canonical(monkeypatch):
    html = """
    <html>
      <head>
        <meta name="twitter:title" content="Twitter Title">
        <meta name="twitter:description" content="Twitter Description">
        <meta name="twitter:image" content="https://cdn.example.com/card.jpg">
        <link rel="canonical" href="/canonical">
        <link rel="icon" href="/favicon.svg">
      </head>
    </html>
    """

    monkeypatch.setattr(
        "pkm_app.services.scraper_service.requests.get",
        lambda *args, **kwargs: _Response(html),
    )

    metadata = ScraperService().extract_metadata("https://example.com/page")

    assert metadata == {
        "og_title": "Twitter Title",
        "og_description": "Twitter Description",
        "thumbnail": "https://cdn.example.com/card.jpg",
        "favicon": "https://example.com/favicon.svg",
        "canonical_url": "https://example.com/canonical",
    }


def test_extract_metadata_returns_youtube_fallback_on_request_error(monkeypatch):
    def _raise_timeout(*args, **kwargs):
        raise requests.Timeout("timeout")

    monkeypatch.setattr("pkm_app.services.scraper_service.requests.get", _raise_timeout)

    assert ScraperService().extract_metadata("https://youtu.be/abc123") == {
        "thumbnail": "https://img.youtube.com/vi/abc123/hqdefault.jpg",
        "canonical_url": "https://www.youtube.com/watch?v=abc123",
        "site_name": "YouTube",
    }


def test_extract_metadata_returns_empty_dict_on_request_error(monkeypatch):
    def _raise_timeout(*args, **kwargs):
        raise requests.Timeout("timeout")

    monkeypatch.setattr("pkm_app.services.scraper_service.requests.get", _raise_timeout)

    assert ScraperService().extract_metadata("https://example.com") == {}


def test_extract_metadata_returns_empty_dict_for_html_without_metadata(monkeypatch):
    monkeypatch.setattr(
        "pkm_app.services.scraper_service.requests.get",
        lambda *args, **kwargs: _Response("<html><head></head></html>"),
    )

    assert ScraperService().extract_metadata("https://example.com") == {}
