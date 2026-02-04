"""
Scans API tests.
"""

import io
import pytest
from PIL import Image, ImageDraw


def create_test_image():
    """Create a simple test image."""
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), "NUTRITION FACTS\nProtein: 25g\nSugar: 5g", fill='black')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    return buffer


@pytest.fixture
async def auth_headers(client, test_user_data):
    """Get authentication headers for a test user."""
    response = await client.post("/api/auth/register", json=test_user_data)
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_categories(client, auth_headers):
    """Test listing categories."""
    response = await client.get("/api/categories", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_list_scans_empty(client, auth_headers):
    """Test listing scans when there are none."""
    response = await client.get("/api/scans", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["data"] == []


@pytest.mark.asyncio
async def test_get_nonexistent_scan(client, auth_headers):
    """Test getting a scan that doesn't exist."""
    response = await client.get("/api/scans/99999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio 
async def test_delete_nonexistent_scan(client, auth_headers):
    """Test deleting a scan that doesn't exist."""
    response = await client.delete("/api/scans/99999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_scans_require_auth(client):
    """Test that scan endpoints require authentication."""
    response = await client.get("/api/scans")
    assert response.status_code == 401
    
    response = await client.post("/api/scans", data={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_bulk_delete_scans(client, auth_headers):
    """Test bulk delete with empty list."""
    response = await client.post(
        "/api/scans/bulk-delete",
        headers=auth_headers,
        json={"ids": []}
    )
    assert response.status_code == 200
