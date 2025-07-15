
def test_register_and_login(client):
    res = client.post("/register", json={"email": "test@example.com", "password": "password"})
    assert res.status_code == 200
    token_res = client.post("/token", data={"username": "test@example.com", "password": "password"})
    assert token_res.status_code == 200
    assert "access_token" in token_res.json()
