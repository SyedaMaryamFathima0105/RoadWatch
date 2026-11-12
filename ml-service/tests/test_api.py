from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
def test_health():
    assert client.get('/health').status_code == 200
def test_rejects_wrong_type():
    response = client.post('/detect', files={'file': ('x.txt', b'hello', 'text/plain')})
    assert response.status_code == 415
