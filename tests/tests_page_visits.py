
def get_token(client):
    client.post("/register", json={"email": "x@y.com", "password": "secret"})
    res = client.post("/token", data={"username": "x@y.com", "password": "secret"})
    return res.json()["access_token"]

def test_add_page_visit(client):
    token = get_token(client)
    res = client.post("/page_visits", json={
        "url": "https://openai.com",
        "title": "OpenAI",
        "visit_time": "2025-07-15T10:00:00"
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["url"] == "https://openai.com"