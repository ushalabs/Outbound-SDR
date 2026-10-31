"""Small public-page fetcher. Resolves, validates and pins every connection's destination."""

import http.client
import ipaddress
import json
import socket
import ssl
import time
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser

import certifi
from bs4 import BeautifulSoup

from app.schemas import domain_of, normalize_url

USER_AGENT = "OutboundSDR/1.0 (local company research; robots-aware)"
MAX_BYTES = 1_000_000


class FetchError(ValueError):
    pass


def public_addresses(host: str, port: int) -> list[str]:
    try:
        addresses = list(
            dict.fromkeys(row[4][0] for row in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM))
        )
    except socket.gaierror as exc:
        raise FetchError("Website hostname could not be resolved") from exc
    if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
        raise FetchError("Private, loopback, reserved and non-public destinations are blocked")
    return addresses


class PinnedHTTP(http.client.HTTPConnection):
    def connect(self):
        addresses = public_addresses(self.host, self.port)
        self.sock = socket.create_connection((addresses[0], self.port), self.timeout)


class PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, context=ssl.create_default_context(cafile=certifi.where()), **kwargs)

    def connect(self):
        addresses = public_addresses(self.host, self.port)
        raw = socket.create_connection((addresses[0], self.port), self.timeout)
        try:
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except (ssl.SSLError, OSError):
            raw.close()
            raise


def request(url: str) -> tuple[int, str, str, str]:
    url = normalize_url(url)
    parsed = urlsplit(url)
    connection_type = PinnedHTTPS if parsed.scheme == "https" else PinnedHTTP
    connection = connection_type(parsed.hostname, port=443 if parsed.scheme == "https" else 80, timeout=10)
    try:
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query
        connection.request(
            "GET",
            path,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,text/plain",
                "Accept-Encoding": "identity",
            },
        )
        response = connection.getresponse()
        if response.status in (301, 302, 303, 307, 308):
            target = response.getheader("Location")
            if not target:
                raise FetchError("Website returned an invalid redirect")
            return response.status, "", "", normalize_url(urljoin(url, target))
        content_type = response.getheader("Content-Type", "").lower()
        if response.getheader("Content-Encoding", "identity").lower() != "identity":
            raise FetchError("Compressed responses are not supported by the safe page fetcher")
        length = response.getheader("Content-Length")
        if length and (not length.isdigit() or int(length) > MAX_BYTES):
            raise FetchError("Website page exceeds the 1 MB limit")
        chunks, size, deadline = [], 0, time.monotonic() + 15
        while True:
            if time.monotonic() > deadline:
                raise FetchError("Website response exceeded the time limit")
            chunk = response.read1(min(16384, MAX_BYTES + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
            if size > MAX_BYTES:
                raise FetchError("Website page exceeds the 1 MB limit")
        raw = b"".join(chunks)
        if len(raw) > MAX_BYTES:
            raise FetchError("Website page exceeds the 1 MB limit")
        return response.status, raw.decode("utf-8", errors="replace"), content_type, url
    except ssl.SSLCertVerificationError as exc:
        raise FetchError("Website TLS certificate verification failed") from exc
    except (OSError, http.client.HTTPException, TimeoutError) as exc:
        raise FetchError("Website request failed or timed out") from exc
    finally:
        connection.close()


@dataclass
class PageEvidence:
    url: str
    title: str
    text: str
    company_name: str | None
    companies: list[dict] = field(default_factory=list)


def structured_companies(soup: BeautifulSoup, page_url: str) -> list[dict]:
    """Read only explicit organization name/URL pairs, including public directory ItemLists."""
    results, seen, nodes = [], set(), 0
    stack = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"})[:20]:
        try:
            stack.append(json.loads(script.get_text()))
        except (ValueError, TypeError, RecursionError):
            continue
    while stack and len(results) < 20 and nodes < 2000:
        item = stack.pop()
        nodes += 1
        if isinstance(item, list):
            stack.extend(item[:200])
        elif isinstance(item, dict):
            kinds = item.get("@type", [])
            kinds = [kinds] if isinstance(kinds, str) else kinds
            if isinstance(kinds, list) and any(
                kind in ("Organization", "Corporation", "LocalBusiness", "ProfessionalService")
                for kind in kinds
            ):
                name, website = item.get("name"), item.get("url")
                if isinstance(name, str) and isinstance(website, str) and name.strip():
                    try:
                        website = normalize_url(urljoin(page_url, website))
                    except ValueError:
                        continue
                    key = domain_of(website)
                    if key not in seen:
                        seen.add(key)
                        results.append(
                            {
                                "company_name": name.strip()[:200],
                                "website_url": website,
                                "evidence": f"Public structured organization metadata: {name.strip()} — {website}",
                            }
                        )
            stack.extend(value for value in item.values() if isinstance(value, (dict, list)))
    return results


def fetch_page(url: str, redirects: int = 0) -> PageEvidence:
    if redirects > 3:
        raise FetchError("Website exceeded the redirect limit")
    url = normalize_url(url)
    parsed = urlsplit(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    for _ in range(4):
        status, robots, _, target = request(robots_url)
        if status not in (301, 302, 303, 307, 308):
            break
        robots_url = target
    else:
        raise FetchError("Website access policy exceeded the redirect limit")
    if not (200 <= status < 300 or status in (404, 410)):
        raise FetchError("Website access policy could not be verified or denies access")
    if 200 <= status < 300:
        policy = RobotFileParser()
        policy.set_url(robots_url)
        policy.parse(robots.splitlines())
        if not policy.can_fetch("OutboundSDR", url):
            raise FetchError("Website robots.txt does not permit this page")
        if policy.crawl_delay("OutboundSDR") or policy.crawl_delay("*"):
            raise FetchError("Website requires a crawl delay; use manual source notes")
    status, html, content_type, final_url = request(url)
    if status in (301, 302, 303, 307, 308):
        # Check the target's policy before retrieving its page, and enforce one global bound.
        return fetch_page(final_url, redirects + 1)
    if not 200 <= status < 300:
        raise FetchError(f"Website returned HTTP {status}; no access restrictions were bypassed")
    if not any(kind in content_type for kind in ("text/html", "text/plain", "application/xhtml+xml")):
        raise FetchError("Only publicly accessible HTML/text pages are supported")
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(" ", strip=True)[:300] if soup.title else (parsed.hostname or "Source")
    site_name = soup.find("meta", attrs={"property": "og:site_name"})
    name = str(site_name.get("content", "")).strip()[:200] if site_name else None
    companies = structured_companies(soup, final_url)
    for element in soup(["script", "style", "noscript", "nav", "footer", "header", "form", "svg"]):
        element.decompose()
    text = " ".join(soup.stripped_strings)[:40000]
    if len(text) < 50:
        raise FetchError("No sufficient readable evidence was found. Use user-provided source notes.")
    return PageEvidence(url=final_url, title=title, text=text, company_name=name or None, companies=companies)
