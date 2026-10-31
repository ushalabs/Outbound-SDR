import pytest
from fastapi import HTTPException

from app.schemas import ProspectInput, domain_of
from app.services.fetching import FetchError, fetch_page, public_addresses
from app.services.prospects import preview_csv

FIXTURE = {
    "company_name": "Isolated fixture",
    "website_url": "https://fixture.invalid",
    "full_name": "Synthetic fixture contact",
}


def test_normalization_and_identity():
    a = ProspectInput(**{**FIXTURE, "website_url": "https://WWW.FIXTURE.INVALID/#fragment"})
    b = ProspectInput(**{**FIXTURE, "email": "fixture@example.com"})
    assert a.identity_key() == b.identity_key()
    assert domain_of(a.website_url) == "fixture.invalid"


@pytest.mark.parametrize("address", ["127.0.0.1", "10.0.0.1", "169.254.169.254", "192.168.1.1", "::1"])
def test_private_destinations_blocked(monkeypatch, address):
    monkeypatch.setattr("socket.getaddrinfo", lambda *args, **kwargs: [(2, 1, 6, "", (address, 443))])
    with pytest.raises(FetchError, match="blocked"):
        public_addresses("fixture.invalid", 443)


def test_robots_denial_and_redirect_limit(monkeypatch):
    monkeypatch.setattr(
        "app.services.fetching.request", lambda url: (200, "User-agent: *\nDisallow: /", "text/plain", url)
    )
    with pytest.raises(FetchError, match="robots"):
        fetch_page("https://fixture.invalid")
    with pytest.raises(FetchError, match="redirect"):
        fetch_page("https://fixture.invalid", redirects=4)


def test_bad_headers():
    with pytest.raises(HTTPException) as exc:
        preview_csv(None, "name\nSynthetic fixture", {})
    assert exc.value.status_code == 422


@pytest.mark.integration
def test_crud_bulk_and_csv(live_client):
    client = live_client
    assert client.get("/api/prospects").json()["total"] == 0
    created = client.post("/api/prospects", json=FIXTURE)
    assert created.status_code == 201, created.text
    record = created.json()
    assert client.get(f"/api/prospects/{record['id']}").json()["company"]["domain"] == "fixture.invalid"
    assert client.post("/api/prospects", json=FIXTURE).status_code == 409
    edited = client.patch(f"/api/prospects/{record['id']}", json={**FIXTURE, "notes": "Updated fixture note"})
    assert edited.status_code == 200
    assert client.get(f"/api/prospects/{record['id']}").json()["notes"] == "Updated fixture note"
    assert client.get("/api/prospects?search=fixture&sort=company&direction=asc").json()["total"] == 1
    assert client.get("/api/prospects?page=999").json()["items"] == []
    assert client.get("/api/prospects?page=0").status_code == 422
    assert (
        client.post("/api/prospects/bulk", json={"ids": [record["id"]], "action": "do_not_contact"}).json()[
            "updated"
        ]
        == 1
    )
    csv_text = "company,website,name\nIsolated fixture,fixture.invalid,Synthetic fixture contact\nSecond fixture,second.invalid,Another synthetic fixture\nBroken,,\n"
    preview = client.post("/api/imports/preview", json={"csv_text": csv_text}).json()
    assert preview["duplicates"] == 1 and len(preview["errors"]) == 1
    imported = client.post(
        "/api/imports/csv", json={"csv_text": csv_text, "filename": "fixture.csv", "confirm": True}
    )
    assert imported.status_code == 201, imported.text
    assert imported.json()["imported_rows"] == 1
    assert (
        client.post("/api/imports/csv", json={"csv_text": csv_text, "confirm": True}).json()["duplicates"]
        == 2
    )
    assert len(client.get(f"/api/companies/{record['company']['id']}").json()["prospects"]) == 1
    assert client.delete(f"/api/prospects/{record['id']}").status_code == 422
    assert client.delete(f"/api/prospects/{record['id']}?confirm=true").status_code == 204
    assert client.get(f"/api/prospects/{record['id']}").status_code == 404


@pytest.mark.integration
def test_public_discovery_live():
    import os

    if os.getenv("RUN_LIVE_TESTS") != "1":
        pytest.skip("Explicit live check required")
    page = fetch_page("https://example.com")
    assert "Example Domain" in page.text
    assert page.url.startswith("https://example.com")
