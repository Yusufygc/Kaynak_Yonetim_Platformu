import socket

import pytest
import requests

from pkm_app.services.scraper_service import ScraperService


@pytest.fixture(autouse=True)
def _fake_dns(monkeypatch):
    """DNS cozumlemesini sahteler: testler gercek ag/DNS'e bagimli olmasin."""

    def _fake_getaddrinfo(host, *args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))]

    monkeypatch.setattr(
        "pkm_app.services.scraper_service.socket.getaddrinfo", _fake_getaddrinfo
    )


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


def _refuse_network_call(*args, **kwargs):
    raise AssertionError("requests.get cagrilmamali - SSRF korumasi engellemeliydi")


@pytest.mark.parametrize(
    ("resolved_ip",),
    [
        ("127.0.0.1",),  # loopback
        ("10.0.0.5",),  # private
        ("169.254.169.254",),  # link-local (bulut metadata servisi)
    ],
)
def test_extract_metadata_blocks_internal_addresses(monkeypatch, resolved_ip):
    monkeypatch.setattr("pkm_app.services.scraper_service.requests.get", _refuse_network_call)
    monkeypatch.setattr(
        "pkm_app.services.scraper_service.socket.getaddrinfo",
        lambda host, *a, **k: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (resolved_ip, 0))],
    )

    assert ScraperService().extract_metadata("http://internal.example/") == {}


def test_extract_metadata_blocks_when_dns_resolution_fails(monkeypatch):
    monkeypatch.setattr("pkm_app.services.scraper_service.requests.get", _refuse_network_call)

    def _raise_gaierror(host, *args, **kwargs):
        raise socket.gaierror("cozumlenemedi")

    monkeypatch.setattr(
        "pkm_app.services.scraper_service.socket.getaddrinfo", _raise_gaierror
    )

    assert ScraperService().extract_metadata("http://does-not-resolve.invalid/") == {}
