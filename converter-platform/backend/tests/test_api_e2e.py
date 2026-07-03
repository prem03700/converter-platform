"""
End-to-end API tests against the real app + a throwaway SQLite DB,
using FastAPI's TestClient. Run with: pytest tests/test_api_e2e.py -v
"""
import io

import pytest
from PIL import Image

# `client` fixture is provided by conftest.py


def _register(client, email="test@example.com"):
    r = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "supersecret123", "full_name": "Test User"},
    )
    assert r.status_code == 201, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login(client):
    headers = _register(client)
    r = client.get("/api/v1/users/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == "test@example.com"


def test_duplicate_registration_rejected(client):
    _register(client, email="dupe@example.com")
    r = client.post(
        "/api/v1/auth/register",
        json={"email": "dupe@example.com", "password": "supersecret123"},
    )
    assert r.status_code == 400


def test_login_with_wrong_password_rejected(client):
    _register(client, email="wrongpw@example.com")
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpw@example.com", "password": "not-the-password"},
    )
    assert r.status_code == 401


def test_upload_requires_auth(client):
    r = client.post("/api/v1/files/upload", files={"file": ("x.png", b"123", "image/png")})
    assert r.status_code == 401


def test_upload_rejects_disallowed_extension(client):
    headers = _register(client, email="badext@example.com")
    r = client.post(
        "/api/v1/files/upload",
        headers=headers,
        files={"file": ("malware.exe", b"MZ\x90\x00", "application/octet-stream")},
    )
    assert r.status_code == 400


def test_full_upload_and_convert_flow(client):
    headers = _register(client, email="flow@example.com")

    img = Image.new("RGB", (40, 40), color=(200, 50, 50))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    r = client.post(
        "/api/v1/files/upload", headers=headers, files={"file": ("photo.png", buf, "image/png")}
    )
    assert r.status_code == 201
    file_id = r.json()["id"]

    r = client.get(f"/api/v1/convert/supported-targets/{file_id}", headers=headers)
    assert r.status_code == 200
    assert "webp" in r.json()["targets"]

    r = client.post("/api/v1/convert", headers=headers, json={"file_id": file_id, "target_format": "webp"})
    assert r.status_code == 202
    conversion = r.json()
    assert conversion["status"] == "completed"

    r = client.get(f"/api/v1/convert/{conversion['id']}/download", headers=headers)
    assert r.status_code == 200
    assert len(r.content) > 0

    r = client.get("/api/v1/history", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 1

    r = client.get("/api/v1/history/stats", headers=headers)
    assert r.status_code == 200
    assert r.json()["total_conversions"] == 1


def test_cannot_convert_to_unsupported_target(client):
    headers = _register(client, email="badtarget@example.com")
    img = Image.new("RGB", (10, 10))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    r = client.post("/api/v1/files/upload", headers=headers, files={"file": ("a.png", buf, "image/png")})
    file_id = r.json()["id"]

    r = client.post("/api/v1/convert", headers=headers, json={"file_id": file_id, "target_format": "mp3"})
    assert r.status_code == 422


def test_users_cannot_access_each_others_files(client):
    headers_a = _register(client, email="usera@example.com")
    headers_b = _register(client, email="userb@example.com")

    img = Image.new("RGB", (10, 10))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    r = client.post("/api/v1/files/upload", headers=headers_a, files={"file": ("a.png", buf, "image/png")})
    file_id = r.json()["id"]

    r = client.get(f"/api/v1/files/{file_id}/download", headers=headers_b)
    assert r.status_code == 404


def test_non_admin_cannot_access_admin_routes(client):
    headers = _register(client, email="notadmin@example.com")
    r = client.get("/api/v1/admin/users", headers=headers)
    assert r.status_code == 403
