"""
테스트 데이터 추가 스크립트
"""
import asyncio
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.database import AsyncSessionLocal
from app.models.page import Page
from app.models.tag import Tag  # Import Tag model to define page_tags
from datetime import datetime


async def seed_data():
    """테스트 데이터 추가"""

    async with AsyncSessionLocal() as session:
        # 샘플 페이지 데이터
        sample_pages = [
            Page(
                slug="characters/player/elon",
                title="엘론 실버스트라이드",
                category="characters/player",
                author="PlayerName",
                content="""# 엘론 실버스트라이드

## 기본 정보
- **종족**: 하이엘프
- **클래스**: 팔라딘 (Oath of Devotion)
- **레벨**: 5

## 배경 스토리
정의를 수호하는 엘프 팔라딘입니다.
""",
                summary="정의를 수호하는 엘프 팔라딘",
                status="active",
                github_sha="abc123",
            ),
            Page(
                slug="locations/cities/silverhold",
                title="실버홀드",
                category="locations/cities",
                author="DM",
                content="""# 실버홀드

## 개요
북부의 주요 도시입니다.

## 역사
오래된 역사를 가지고 있습니다.
""",
                summary="북부의 주요 도시",
                status="active",
                github_sha="def456",
            ),
            Page(
                slug="items/weapons/holy-sword",
                title="성검 라이트브링어",
                category="items/weapons",
                author="DM",
                content="""# 성검 라이트브링어

## 능력
- 언데드에게 추가 피해
- 어둠을 밝히는 빛

## 역사
전설적인 팔라딘이 사용했던 검입니다.
""",
                summary="전설적인 성검",
                status="active",
                github_sha="ghi789",
            ),
        ]

        # DB에 추가
        session.add_all(sample_pages)
        await session.commit()

        print(f"Added {len(sample_pages)} sample pages successfully.")


if __name__ == "__main__":
    print("Seeding test data...")
    asyncio.run(seed_data())
    print("Completed!")
