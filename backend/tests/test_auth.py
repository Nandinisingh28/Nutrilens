"""
Authentication API tests.
"""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health endpoint returns healthy status."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_user(client, test_user_data):
    """Test user registration."""
    response = await client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["user"]["email"] == test_user_data["email"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client, test_user_data):
    """Test registration with duplicate email fails."""
    # First registration
    await client.post("/api/auth/register", json=test_user_data)
    
    # Second registration with same email
    response = await client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client, test_user_data, test_user_login):
    """Test user login with correct credentials."""
    # Register first
    await client.post("/api/auth/register", json=test_user_data)
    
    # Login
    response = await client.post("/api/auth/login", json=test_user_login)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user_data):
    """Test login with wrong password fails."""
    # Register first
    await client.post("/api/auth/register", json=test_user_data)
    
    # Login with wrong password
    response = await client.post("/api/auth/login", json={
        "email": test_user_data["email"],
        "password": "WrongPassword123",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """Test login with nonexistent email fails."""
    response = await client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "SomePassword123",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client, test_user_data):
    """Test getting current user with valid token."""
    # Register and get token
    reg_response = await client.post("/api/auth/register", json=test_user_data)
    token = reg_response.json()["data"]["access_token"]
    
    # Get current user
    response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["email"] == test_user_data["email"]


@pytest.mark.asyncio
async def test_protected_route_without_token(client):
    """Test that protected routes require authentication."""
    response = await client.get("/api/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_token_refresh(client, test_user_data):
    """Test token refresh."""
    # Register and get tokens
    reg_response = await client.post("/api/auth/register", json=test_user_data)
    refresh_token = reg_response.json()["data"]["refresh_token"]
    
    # Refresh token
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data["data"]
