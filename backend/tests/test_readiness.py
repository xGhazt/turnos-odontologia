from app.core.health import check_database, check_redis


async def test_readiness_all_dependencies_ok(app, client):
    app.dependency_overrides[check_database] = lambda: True
    app.dependency_overrides[check_redis] = lambda: True

    response = await client.get("/api/health/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["dependencies"] == {"database": "ok", "redis": "ok"}


async def test_readiness_degraded_when_redis_down(app, client):
    app.dependency_overrides[check_database] = lambda: True
    app.dependency_overrides[check_redis] = lambda: False

    response = await client.get("/api/health/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["dependencies"]["redis"] == "unavailable"


async def test_readiness_degraded_when_all_down(app, client):
    app.dependency_overrides[check_database] = lambda: False
    app.dependency_overrides[check_redis] = lambda: False

    response = await client.get("/api/health/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
