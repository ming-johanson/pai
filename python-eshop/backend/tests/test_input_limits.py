import pytest

from db.seed import DEMO_EMAIL, DEMO_PASSWORD
from tests.conftest import login

LIMIT = 99


def change_password(client, headers, new_password, current_password=DEMO_PASSWORD):
    return client.post(
        "/api/auth/password",
        json={"current_password": current_password, "new_password": new_password},
        headers=headers,
    )


def test_over_long_password_is_refused_with_a_clear_message(client, demo_headers):
    response = change_password(client, demo_headers, "x" * 90)

    assert response.status_code == 422
    message = str(response.json()["detail"])
    assert "72" in message
    assert "truncate" not in message


def test_multibyte_password_over_72_bytes_is_refused(client, demo_headers):
    assert change_password(client, demo_headers, "é" * 40).status_code == 422


@pytest.mark.parametrize("length", [71, 72])
def test_passwords_at_the_limit_still_work(client, demo_headers, length):
    password = "p" * length

    assert change_password(client, demo_headers, password).status_code == 204
    login(client, DEMO_EMAIL, password)


def test_over_long_password_at_login_is_just_wrong(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "demouser@perthai.com.au", "password": "x" * 200},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def add(client, headers, quantity, item=1):
    return client.post(
        "/api/basket/items",
        json={"catalog_item_id": item, "quantity": quantity},
        headers=headers,
    )


def test_quantity_above_the_limit_is_refused(client, demo_headers):
    assert add(client, demo_headers, 1_000_000_000).status_code == 422
    assert add(client, demo_headers, LIMIT + 1).status_code == 422
    assert add(client, demo_headers, LIMIT).status_code == 200


def test_adding_cannot_push_a_line_over_the_limit(client, demo_headers):
    add(client, demo_headers, LIMIT - 1)

    response = add(client, demo_headers, 5)

    assert response.status_code == 400
    assert str(LIMIT) in response.json()["detail"]


def test_bulk_update_enforces_the_same_bounds(client, demo_headers):
    basket = add(client, demo_headers, 2).json()
    line = str(basket["items"][0]["id"])

    def put(quantity):
        return client.put(
            "/api/basket/items", json={"quantities": {line: quantity}}, headers=demo_headers
        )

    assert put(LIMIT + 1).status_code == 422
    assert put(-1).status_code == 422
    assert put(LIMIT).json()["item_count"] == LIMIT
    assert put(0).json()["items"] == []
