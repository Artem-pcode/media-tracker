import pytest
from httpx import AsyncClient, Response


@pytest.fixture
def sample_title_data():
    return {"name": "Test Movie", "content_type": "movie", "year": 2020}


def test_sample_data_title(sample_title_data):
    assert sample_title_data["year"] == 2020


def is_valid_year(year: int) -> bool:
    if not isinstance(year, int):
        raise TypeError("year is not integer")
    if year >= 1888 and year <= 2100:
        return True
    return False


@pytest.mark.parametrize("year, expect",[
    (2000, True),
    (1000, False),
    (2200, False),
    (1888, True)
])
def test_valid_year(year, expect):
    assert is_valid_year(year) == expect


def test_valid_year_raise():
    with pytest.raises(TypeError):
        is_valid_year("str")


async def test_root(client: AsyncClient):
    response: Response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "MediaTracker API is running"}


async def test_get_nonexistent_title(client: AsyncClient):
    response: Response = await client.get(url="/titles/99999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Title not found"}


async def test_create_title(client: AsyncClient):
    response: Response = await client.post("/titles", json={
        "name": "Movie",
        "content_type": "movie",
        "year": 2020
    })
    assert response.status_code == 401