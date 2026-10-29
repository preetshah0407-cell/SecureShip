import app

def test_home():
    response = app.app.test_client().get("/")
    assert response.status_code == 200
    assert response.json["project"] == "SecureShip"

def test_health():
    response = app.app.test_client().get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"
