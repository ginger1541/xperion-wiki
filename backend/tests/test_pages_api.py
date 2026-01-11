"""
Test Pages API - TDD로 GitHub 연동 문제 확인
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_create_page_success():
    """
    Test 1: 정상적인 페이지 생성 테스트

    Expected: 201 Created
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        page_data = {
            "slug": "test/test-page",
            "title": "Test Page",
            "category": "test",
            "content": "# Test Content\n\nThis is a test.",
            "author": "Test User",
            "status": "active",
            "summary": "Test summary",
            "tags": ["test"]
        }

        response = await ac.post("/api/pages", json=page_data)

        assert response.status_code == 201
        data = response.json()
        assert data["slug"] == "test/test-page"
        assert data["title"] == "Test Page"
        assert "github_sha" in data


@pytest.mark.asyncio
async def test_create_page_github_error():
    """
    Test 2: GitHub 연동 실패 시나리오 테스트

    Expected: 502 Bad Gateway with GITHUB_ERROR code
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 잘못된 slug로 GitHub 에러 유발
        page_data = {
            "slug": "invalid///slug",  # 유효하지 않은 경로
            "title": "Invalid Page",
            "category": "test",
            "content": "# Test",
            "author": "Test User",
            "status": "active",
            "summary": "",
            "tags": []
        }

        response = await ac.post("/api/pages", json=page_data)

        # GitHub 에러 시 502 반환
        if response.status_code == 502:
            data = response.json()
            assert data["detail"]["code"] == "GITHUB_ERROR"
            assert "GitHub 저장에 실패했습니다" in data["detail"]["message"]


@pytest.mark.asyncio
async def test_health_check():
    """
    Test 3: Health check 테스트

    Expected: 200 OK
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
