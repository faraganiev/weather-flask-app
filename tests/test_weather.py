import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from weather_api import get_weather_for_city
from history_store import (
    log_city_search,
    get_city_stats,
    get_user_stats
)
from app import app as flask_app

# ------------ Погодные тесты ------------

def test_weather_valid_city():
    result = get_weather_for_city("Tashkent")
    assert "temperature" in result
    assert "windspeed" in result
    assert "time" in result
    assert result["city"].lower() == "tashkent"

def test_weather_invalid_city():
    result = get_weather_for_city("InvalidCityXYZ123")
    assert "error" in result

# ------------ История ------------

def test_history_logging():
    fake_user = "test-user-123"
    log_city_search("Tashkent", fake_user)
    log_city_search("Tashkent", fake_user)

    user_stats = get_user_stats(fake_user)
    assert user_stats["tashkent"] >= 2

    global_stats = get_city_stats()
    assert global_stats["tashkent"] >= 2

# ------------ API тесты ------------

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

def test_api_stats(client):
    response = client.get("/api/stats")
    assert response.status_code == 200
    assert isinstance(response.get_json(), dict)

def test_api_user_stats(client):
    user_id = "test-user-123"

    # Отправим POST с нужной cookie
    response = client.post("/", data={"city": "Tashkent"}, headers={"Cookie": f"user_id={user_id}"})
    assert response.status_code == 200

    # Теперь проверим API
    response = client.get("/api/user_stats", headers={"Cookie": f"user_id={user_id}"})
    assert response.status_code == 200
    data = response.get_json()

    assert isinstance(data, dict)
    assert "tashkent" in data

