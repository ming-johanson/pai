from db.seed import (
    ORGANISER_EMAIL,
    ORGANISER_PASSWORD,
    SUPPLIER_EMAIL,
    SUPPLIER_PASSWORD,
)
from tests.conftest import login


def test_seeded_organiser_signs_in_with_organiser_role(client):
    response = client.post(
        "/api/auth/login",
        json={"email": ORGANISER_EMAIL, "password": ORGANISER_PASSWORD},
    )

    assert response.status_code == 200, response.text
    assert response.json()["role"] == "organiser"


def test_seeded_supplier_signs_in_with_supplier_role(client):
    headers = login(client, SUPPLIER_EMAIL, SUPPLIER_PASSWORD)

    me = client.get("/api/auth/me", headers=headers).json()

    assert me == {"email": SUPPLIER_EMAIL, "role": "supplier"}


def test_demo_user_is_a_rep(client, demo_headers):
    assert client.get("/api/auth/me", headers=demo_headers).json()["role"] == "rep"


def test_nothing_is_public_without_a_token(client):
    for method, path in [
        ("GET", "/api/catalog/items"),
        ("GET", "/api/catalog/types"),
        ("GET", "/api/basket"),
        ("POST", "/api/basket/items"),
        ("GET", "/api/orders"),
        ("GET", "/api/auth/me"),
    ]:
        response = client.request(method, path, json={"catalog_item_id": 1})
        assert response.status_code == 401, f"{method} {path} -> {response.status_code}"


def test_health_and_login_stay_open(client):
    assert client.get("/api/health").status_code == 200
    bad_login = client.post(
        "/api/auth/login", json={"email": "nobody@example.com", "password": "x"}
    )
    assert bad_login.status_code == 401


def test_there_is_no_register_endpoint(client):
    response = client.post(
        "/api/auth/register", json={"email": "new@example.com", "password": "secret123"}
    )

    assert response.status_code == 404


def test_anonymous_basket_header_is_not_a_credential(client):
    import uuid

    response = client.get("/api/basket", headers={"X-Basket-Id": str(uuid.uuid4())})

    assert response.status_code == 401


def organiser_headers(client):
    return login(client, ORGANISER_EMAIL, ORGANISER_PASSWORD)


def test_organiser_creates_an_account_the_new_user_can_sign_in_with(client):
    response = client.post(
        "/api/organiser/users",
        json={"email": "rep@acme.example", "password": "acme-secret", "role": "rep"},
        headers=organiser_headers(client),
    )

    assert response.status_code == 201, response.text
    assert response.json() == {"email": "rep@acme.example", "role": "rep"}
    headers = login(client, "rep@acme.example", "acme-secret")
    assert client.get("/api/auth/me", headers=headers).json()["role"] == "rep"


def test_organiser_can_create_any_role(client):
    for role in ["organiser", "supplier"]:
        response = client.post(
            "/api/organiser/users",
            json={"email": f"{role}2@perthai.com.au", "password": "secret123", "role": role},
            headers=organiser_headers(client),
        )
        assert response.status_code == 201, response.text
        assert response.json()["role"] == role


def test_unknown_role_is_refused(client):
    response = client.post(
        "/api/organiser/users",
        json={"email": "x@example.com", "password": "secret123", "role": "admin"},
        headers=organiser_headers(client),
    )

    assert response.status_code == 422


def test_duplicate_email_is_refused(client):
    response = client.post(
        "/api/organiser/users",
        json={"email": SUPPLIER_EMAIL, "password": "secret123", "role": "rep"},
        headers=organiser_headers(client),
    )

    assert response.status_code == 409


def test_rep_and_supplier_get_403_on_organiser_routes(client, demo_headers):
    body = {"email": "x@example.com", "password": "secret123", "role": "rep"}

    for headers in [demo_headers, login(client, SUPPLIER_EMAIL, SUPPLIER_PASSWORD)]:
        response = client.post("/api/organiser/users", json=body, headers=headers)
        assert response.status_code == 403, response.text
    assert client.post("/api/organiser/users", json=body).status_code == 401


def test_any_signed_in_user_can_change_their_password(client):
    headers = login(client, SUPPLIER_EMAIL, SUPPLIER_PASSWORD)

    response = client.post(
        "/api/auth/password",
        json={"current_password": SUPPLIER_PASSWORD, "new_password": "new-secret-9"},
        headers=headers,
    )

    assert response.status_code == 204, response.text
    login(client, SUPPLIER_EMAIL, "new-secret-9")
    old = client.post(
        "/api/auth/login", json={"email": SUPPLIER_EMAIL, "password": SUPPLIER_PASSWORD}
    )
    assert old.status_code == 401


def test_wrong_current_password_changes_nothing(client, demo_headers):
    from db.seed import DEMO_EMAIL, DEMO_PASSWORD

    response = client.post(
        "/api/auth/password",
        json={"current_password": "not-it", "new_password": "new-secret-9"},
        headers=demo_headers,
    )

    assert response.status_code == 400
    login(client, DEMO_EMAIL, DEMO_PASSWORD)


def test_token_for_a_deleted_user_is_a_401_not_a_crash(client):
    from db.seed import DEMO_EMAIL
    from tests.test_basket_identity import make_token

    headers = {"Authorization": f"Bearer {make_token(sub='ghost@example.com')}"}

    assert client.get("/api/auth/me", headers=headers).status_code == 401
    assert client.post("/api/organiser/users", json={
        "email": "x@example.com", "password": "secret123", "role": "rep"
    }, headers=headers).status_code == 401
    assert DEMO_EMAIL  # the demo user is untouched by this test


def test_older_databases_gain_roles_and_the_new_accounts(tmp_path, monkeypatch):
    import sqlite3

    from fastapi.testclient import TestClient

    from config import settings

    old = tmp_path / "old.db"
    conn = sqlite3.connect(old)
    conn.executescript(
        """
        CREATE TABLE catalog_brands (id INTEGER PRIMARY KEY AUTOINCREMENT, brand TEXT NOT NULL);
        CREATE TABLE catalog_types (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT NOT NULL);
        CREATE TABLE catalog_items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
          description TEXT NOT NULL, price REAL NOT NULL, picture_uri TEXT NOT NULL,
          catalog_brand_id INTEGER NOT NULL, catalog_type_id INTEGER NOT NULL);
        CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL UNIQUE,
          password_hash TEXT NOT NULL);
        INSERT INTO catalog_brands (brand) VALUES ('Old');
        INSERT INTO catalog_types (type) VALUES ('Mug');
        INSERT INTO catalog_items VALUES (1, 'Mug', 'Mug', 1.0, '/static/images/products/1.png', 1, 1);
        INSERT INTO users (email, password_hash) VALUES ('old@example.com', 'x');
        """
    )
    conn.commit()
    conn.close()
    monkeypatch.setattr(settings, "database_path", str(old))
    from main import app

    with TestClient(app) as client:
        assert login(client, ORGANISER_EMAIL, ORGANISER_PASSWORD)
        assert login(client, SUPPLIER_EMAIL, SUPPLIER_PASSWORD)
    conn = sqlite3.connect(old)
    role = conn.execute("SELECT role FROM users WHERE email = 'old@example.com'").fetchone()[0]
    assert role == "rep"
