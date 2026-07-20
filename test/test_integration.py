from httpx import AsyncClient, Response
from typing import Dict

async def test_create_titles_w_auth(client: AsyncClient, auth_headers: Dict):
    response: Response = await client.post(
        "/titles",
        json={
            "name": "SpiderMan",
            "content_type": "movie",
            "year": 2026
        },
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "SpiderMan"
    assert data["type"] == "movie"
    assert data["year"] == 2026
    assert "id" in data


async def test_duplicate_registration_fails(client: AsyncClient):
    await client.post("/register", json={"email": "str", "password": "12345678"})
    response = await client.post("/register", json={"email": "str", "password": "12345678"})
    assert response.status_code == 409


async def test_login_with_wrong_password_fails(client: AsyncClient):
    await client.post("/register", json={"email": "str", "password": "12345678"})
    response = await client.post("/login", data={"username": "str", "password": "123456789"})
    assert response.status_code == 401


async def test_update_nonexistent_title_return_404(client: AsyncClient, auth_headers: Dict):
    response = await client.put(
        "/titles/999999",
        json={
            "name": "Son",
            "content_type": "movie",
            "year": 2000
        },
        headers=auth_headers
    )
    assert response.status_code == 404


async def test_titles_list_reflects_new_title(client: AsyncClient, auth_headers: Dict):
    first_response = await client.get("/titles")
    len_first_res = len(first_response.json())

    await client.post(
        "/titles",
        json={
            "name": "Son",
            "content_type": "movie",
            "year": 2000
        },
        headers=auth_headers     
    )

    sec_response = await client.get("/titles")
    len_sec_response = len(sec_response.json())
    assert len_first_res + 1 == len_sec_response