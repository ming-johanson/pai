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
