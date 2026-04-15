import pytest

from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_hello(client):
    response = client.get("/hello/Alice")
    assert response.status_code == 200
    assert "Alice" in response.get_json()["message"]


def test_not_found(client):
    response = client.get("/page-inexistante")
    assert response.status_code == 404


def test_add(client):
    response = client.get("/add/3/5")
    assert response.status_code == 200
    assert response.get_json()["result"] == 8


def test_about(client):
    response = client.get("/about")
    assert response.status_code == 200
    assert response.get_json()["version"] == "1.0"


# Tests supplémentaires pour améliorer la couverture


def test_hello_empty_name(client):
    response = client.get("/hello/")
    assert response.status_code == 404  # Flask retourne 404 pour les routes non définies


def test_hello_special_characters(client):
    response = client.get("/hello/Jean-Pierre%20O'Connor")
    assert response.status_code == 200
    data = response.get_json()
    assert "Jean-Pierre O'Connor" in data["message"]


def test_hello_long_name(client):
    long_name = "A" * 1000
    response = client.get(f"/hello/{long_name}")
    assert response.status_code == 200
    data = response.get_json()
    assert long_name in data["message"]


def test_hello_name_with_spaces(client):
    response = client.get("/hello/Jean%20Pierre")
    assert response.status_code == 200
    data = response.get_json()
    assert "Jean Pierre" in data["message"]


def test_add_negative_numbers(client):
    # Flask's int converter ne supporte pas les nombres négatifs dans les URLs
    response = client.get("/add/-3/-5")
    assert response.status_code == 404


def test_add_zero_values(client):
    response = client.get("/add/0/0")
    assert response.status_code == 200
    assert response.get_json()["result"] == 0

    response = client.get("/add/5/0")
    assert response.status_code == 200
    assert response.get_json()["result"] == 5


def test_add_large_numbers(client):
    response = client.get("/add/1000000/2000000")
    assert response.status_code == 200
    assert response.get_json()["result"] == 3000000


def test_add_mixed_signs(client):
    # Flask's int converter ne supporte pas les nombres négatifs dans les URLs
    response = client.get("/add/10/-5")
    assert response.status_code == 404


def test_home_post_method(client):
    response = client.post("/")
    assert response.status_code == 405  # Method Not Allowed


def test_health_post_method(client):
    response = client.post("/health")
    assert response.status_code == 405


def test_hello_post_method(client):
    response = client.post("/hello/Alice")
    assert response.status_code == 405


def test_add_post_method(client):
    response = client.post("/add/3/5")
    assert response.status_code == 405


def test_about_post_method(client):
    response = client.post("/about")
    assert response.status_code == 405


def test_home_put_method(client):
    response = client.put("/")
    assert response.status_code == 405


def test_home_delete_method(client):
    response = client.delete("/")
    assert response.status_code == 405


def test_response_content_type_json(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.content_type == "application/json"

    response = client.get("/health")
    assert response.content_type == "application/json"

    response = client.get("/hello/Alice")
    assert response.content_type == "application/json"

    response = client.get("/add/1/2")
    assert response.content_type == "application/json"

    response = client.get("/about")
    assert response.content_type == "application/json"


def test_add_invalid_integer_conversion(client):
    # Test avec des valeurs non entières dans l'URL - Flask retourne 404
    response = client.get("/add/abc/5")
    assert response.status_code == 404

    response = client.get("/add/5/def")
    assert response.status_code == 404

    response = client.get("/add/3.5/2")
    assert response.status_code == 404


def test_multiple_slashes(client):
    # Test avec des slashes multiples - Flask redirige // vers /
    response = client.get("//")
    assert response.status_code == 308  # Permanent Redirect

    # Test avec trailing slash sur une route existante - Flask est strict sur les slashes
    response = client.get("/health/")
    assert response.status_code == 404
