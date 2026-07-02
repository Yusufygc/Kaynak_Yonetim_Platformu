import ipaddress
import socket
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from core.logger import log


class ScraperService:
    """URL metadata extraction service for rich link cards."""

    _TIMEOUT_SECONDS = 5
    _HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    def extract_metadata(self, url: str) -> dict:
        if self._is_blocked_host(url):
            log.warning("URL ic ag/loopback adresine cozumlendigi icin reddedildi: %s", url)
            return self._platform_fallback(url)

        try:
            response = requests.get(
                url,
                headers=self._HEADERS,
                timeout=self._TIMEOUT_SECONDS,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            log.warning("URL metadata alinamadi: %s - %s", url, exc)
            return self._platform_fallback(url)

        try:
            metadata = self._parse_html(response.text, response.url)
            return {**self._platform_fallback(response.url), **metadata}
        except Exception as exc:
            log.warning("URL metadata parse edilemedi: %s - %s", url, exc)
            return self._platform_fallback(url)

    def _parse_html(self, html: str, base_url: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")

        metadata = {
            "og_title": self._content(soup, "property", "og:title")
            or self._content(soup, "name", "twitter:title")
            or self._content(soup, "property", "twitter:title")
            or self._text(soup.find("title")),
            "og_description": self._content(soup, "property", "og:description")
            or self._content(soup, "name", "twitter:description")
            or self._content(soup, "property", "twitter:description")
            or self._content(soup, "name", "description"),
            "thumbnail": self._absolute(
                self._content(soup, "property", "og:image")
                or self._content(soup, "name", "twitter:image")
                or self._content(soup, "property", "twitter:image"),
                base_url,
            ),
            "favicon": self._absolute(self._favicon(soup), base_url),
            "canonical_url": self._absolute(self._link_href(soup, "canonical"), base_url),
            "site_name": self._content(soup, "property", "og:site_name"),
        }
        return {key: value for key, value in metadata.items() if value}

    @staticmethod
    def _content(soup: BeautifulSoup, attr_name: str, attr_value: str) -> str | None:
        tag = soup.find("meta", attrs={attr_name: attr_value})
        if tag is None:
            return None
        value = tag.get("content")
        return value.strip() if isinstance(value, str) and value.strip() else None

    @staticmethod
    def _text(tag) -> str | None:
        if tag is None:
            return None
        value = tag.get_text(strip=True)
        return value or None

    @staticmethod
    def _favicon(soup: BeautifulSoup) -> str | None:
        expected = {"icon", "shortcut", "apple-touch-icon"}
        for tag in soup.find_all("link"):
            rel_values = tag.get("rel") or []
            if isinstance(rel_values, str):
                rel_values = rel_values.split()
            if not expected.intersection(rel_values):
                continue
            href = tag.get("href")
            if isinstance(href, str) and href.strip():
                return href.strip()
        return None

    @staticmethod
    def _link_href(soup: BeautifulSoup, rel: str) -> str | None:
        tag = soup.find("link", rel=rel)
        if tag is None:
            return None
        href = tag.get("href")
        return href.strip() if isinstance(href, str) and href.strip() else None

    @staticmethod
    def _is_blocked_host(url: str) -> bool:
        """Ic ag / loopback / link-local adreslere istek atilmasini engeller (SSRF)."""
        hostname = urlparse(url).hostname
        if not hostname:
            return True
        try:
            addresses = {info[4][0] for info in socket.getaddrinfo(hostname, None)}
        except socket.gaierror:
            return True
        for address in addresses:
            ip = ipaddress.ip_address(address)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                return True
        return False

    @staticmethod
    def _absolute(value: str | None, base_url: str) -> str | None:
        if not value:
            return None
        return urljoin(base_url, value)

    def _platform_fallback(self, url: str) -> dict:
        youtube_id = self._youtube_video_id(url)
        if not youtube_id:
            return {}
        return {
            "thumbnail": f"https://img.youtube.com/vi/{youtube_id}/hqdefault.jpg",
            "canonical_url": f"https://www.youtube.com/watch?v={youtube_id}",
            "site_name": "YouTube",
        }

    @staticmethod
    def _youtube_video_id(url: str) -> str | None:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if host.startswith("www."):
            host = host[4:]
        if host == "youtu.be":
            video_id = parsed.path.strip("/").split("/")[0]
            return video_id or None
        if host.endswith("youtube.com"):
            query_id = parse_qs(parsed.query).get("v", [None])[0]
            if query_id:
                return query_id
            parts = [part for part in parsed.path.split("/") if part]
            if len(parts) >= 2 and parts[0] in {"shorts", "embed"}:
                return parts[1]
        return None
