"""
데이터베이스 연결 설정
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# 비동기 엔진 생성
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",  # 개발 환경에서만 SQL 로그 출력
    future=True,
)

# 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base 클래스 (모델들이 상속받을 기본 클래스)
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    데이터베이스 세션 의존성
    FastAPI 엔드포인트에서 사용
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
