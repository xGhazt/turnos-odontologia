async def test_liveness_returns_ok(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_unknown_route_returns_404(client):
    response = await client.get("/api/healthz")
    assert response.status_code == 404
