from datetime import datetime, timedelta, timezone

from jose import jwt

from config import settings
from db.seed import DEMO_EMAIL
from tests.conftest import login


def basket_of(client, headers):
    return client.get("/api/basket", headers=headers).json()


def test_signed_in_shopper_can_manage_their_basket(client, demo_headers):
    basket = client.post(
        "/api/basket/items", json={"catalog_item_id": 4, "quantity": 2}, headers=demo_headers
    ).json()
    line = str(basket["items"][0]["id"])

    updated = client.put(
        "/api/basket/items", json={"quantities": {line: 3}}, headers=demo_headers
    ).json()
    assert updated["item_count"] == 3


def make_token(**overrides):
    payload = {"sub": DEMO_EMAIL, "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
    payload.update(overrides)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def test_expired_token_is_rejected(client):
    expired = make_token(exp=datetime.now(timezone.utc) - timedelta(minutes=1))
    headers = {"Authorization": f"Bearer {expired}"}

    response = client.get("/api/basket", headers=headers)

    assert response.status_code == 401


def test_tampered_token_is_rejected(client):
    token = make_token()
    tampered = token[:-4] + ("AAAA" if not token.endswith("AAAA") else "BBBB")
    for value in [f"Bearer {tampered}", "Bearer not.a.token", "Basic abc"]:
        response = client.get(
            "/api/basket", headers={"Authorization": value}
        )
        assert response.status_code == 401, value


def test_expired_token_is_rejected_on_orders(client):
    expired = make_token(exp=datetime.now(timezone.utc) - timedelta(minutes=1))

    response = client.get("/api/orders", headers={"Authorization": f"Bearer {expired}"})

    assert response.status_code == 401


def test_basket_survives_an_expired_session(client, demo_headers):
    client.post("/api/basket/items", json={"catalog_item_id": 6}, headers=demo_headers)

    headers = login(client)

    assert basket_of(client, headers)["item_count"] == 1
