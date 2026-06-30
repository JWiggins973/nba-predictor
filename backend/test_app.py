from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app import app
import app as var
from config import MAX_DAILY_CALLS

client = TestClient(app)


# setup once before all tests
def setup_module():
    client.__enter__()


# tear down app after all tests
def teardown_module():
    client.__exit__(None, None, None)


# test predict endpoint
def test_predict_good_response():
    response = client.get("/predict/LeBron James")
    assert response.status_code == 200
    data = response.json()
    assert "predicted_ppg" in data
    assert "last_season" in data
    assert "actual_ppg" in data
    assert "last_season_stats" in data
    assert "last_season_stats_1" in data
    assert "last_season_stats_2" in data
    assert "actual_stats" in data
    assert "top_shap_values" in data
    assert len(data["top_shap_values"]) == 3
    print("Test /predict with valid player passed!")


# test predict endpoint with invalid player
def test_predict_bad_response():
    response = client.get("/predict/Fake Player")
    assert response.status_code == 404
    print("Test /predict with Fake Player passed!")


# Test the explain endpoint with a valid player
def test_explain_good_response(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key-for-test")

    fake_response = MagicMock()
    fake_response.text = "fake explanation"

    with patch("app.genai.Client") as mock_client_class:
        mock_client_class.return_value.models.generate_content.return_value = (
            fake_response
        )
        response = client.get("/explain/Stephen Curry")

    assert response.status_code == 200
    data = response.json()
    assert data == {"explanation": "fake explanation"}
    print("Test /explain with valid player passed!")


# Test the explain endpoint with an invalid player
def test_explain_bad_response():
    response = client.get("/explain/Fake Player")
    assert response.status_code == 404
    print("Test /explain with Fake Player passed!")


# Test the API key
def test_explain_no_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = client.get("/explain/LeBron James")
    assert response.json() == {"explanation": "GEMINI_API_KEY is not set."}
    print("Test /explain with no API key passed!")


# Test the maximum number of calls
def test_explain_max_calls():
    var.daily_counter = MAX_DAILY_CALLS
    response = client.get("/explain/LeBron James")
    assert response.status_code == 429
    print("Test /explain with max calls passed!")
