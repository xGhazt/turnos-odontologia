ALLOWED_ORIGIN = "http://localhost:5173"


async def test_cors_preflight_from_allowed_origin(client):
    response = await client.options(
        "/api/health",
        headers={
            "Origin": ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") == ALLOWED_ORIGIN


async def test_cors_preflight_from_disallowed_origin(client):
    response = await client.options(
        "/api/health",
        headers={
            "Origin": "http://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in response.headers
