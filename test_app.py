from fastapi.testclient import TestClient
from app import app

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
    print("Test /predict with valid player passed!")


# test predict endpoint with invalid player
def test_predict_bad_response():
    response = client.get("/predict/Fake Player")
    assert response.status_code == 404
    print("Test /predict with Fake Player passed!")
