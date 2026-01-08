"""
Xperion Wiki - FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="D&D TRPG 위키 시스템 API",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """루트 엔드포인트 - API 상태 확인"""
    return {
        "message": "Xperion Wiki API",
        "version": settings.VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}


# API 라우터 등록
from app.api import projects, pages, search, tags, upload

app.include_router(projects.router, tags=["projects"])
app.include_router(pages.router, prefix="/api/pages", tags=["pages"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 개발 중 자동 재시작
    )
