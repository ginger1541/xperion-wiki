# 빠른 시작 가이드

## 1. 환경 설정

### 1.1 가상환경 생성 및 활성화

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 1.2 패키지 설치

```bash
pip install -r requirements.txt
```

### 1.3 환경 변수 설정

```bash
# .env.example을 .env로 복사
copy .env.example .env

# .env 파일 내용 (최소 설정)
DATABASE_URL=postgresql+asyncpg://admin:password@localhost:5432/xperion_wiki
GITHUB_TOKEN=your_token_here
GITHUB_REPO=username/xperion-wiki-content
GITHUB_BRANCH=main
SECRET_KEY=your-secret-key-change-this
CORS_ORIGINS=http://localhost:5173
ENVIRONMENT=development
```

## 2. PostgreSQL 실행 (Docker)

```bash
docker run -d \
  --name xperion-wiki-db \
  -e POSTGRES_DB=xperion_wiki \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15
```

## 3. 데이터베이스 마이그레이션

```bash
# 마이그레이션 적용
alembic upgrade head
```

## 4. 테스트 데이터 추가 (선택사항)

```bash
python scripts/seed_data.py
```

## 5. 서버 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 6. API 테스트

### 브라우저에서 확인

- http://localhost:8000 → 루트 엔드포인트
- http://localhost:8000/docs → Swagger UI (API 문서)
- http://localhost:8000/api/pages → 페이지 목록

### curl로 테스트

```bash
# 헬스 체크
curl http://localhost:8000/health

# 페이지 목록
curl http://localhost:8000/api/pages

# 특정 페이지 조회
curl http://localhost:8000/api/pages/characters/player/elon
```

## 문제 해결

### PostgreSQL 연결 오류

```bash
# PostgreSQL이 실행 중인지 확인
docker ps | grep xperion-wiki-db

# 로그 확인
docker logs xperion-wiki-db
```

### 마이그레이션 오류

```bash
# 현재 마이그레이션 상태 확인
alembic current

# 마이그레이션 히스토리 확인
alembic history
```

### 모듈 import 오류

```bash
# 가상환경이 활성화되었는지 확인
which python  # Linux/Mac
where python  # Windows

# 패키지 재설치
pip install -r requirements.txt --force-reinstall
```

## 다음 단계

1. POST /api/pages 구현 (문서 생성)
2. PUT /api/pages/{slug} 구현 (문서 수정)
3. GitHub API 연동
4. 검색 기능 추가
