# 지금 바로 실행하기

## 1. 환경 설정 (5분)

### 1.1 가상환경 및 패키지 설치

```bash
cd backend

# 가상환경 생성
python -m venv venv

# Windows
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 1.2 환경 변수 설정

```bash
# .env 파일 생성
copy .env.example .env
```

`.env` 파일을 열어서 수정:

```env
# 최소 필수 설정
DATABASE_URL=postgresql+asyncpg://admin:password@localhost:5432/xperion_wiki
GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GITHUB_REPO=your-username/xperion-wiki-content
SECRET_KEY=change-this-to-random-string-12345
```

**GitHub Token 발급 방법:**
1. GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. "Generate new token" 클릭
3. Repository access: `xperion-wiki-content` 선택
4. Permissions:
   - Contents: Read and write
5. 생성된 토큰을 `.env`의 `GITHUB_TOKEN`에 붙여넣기

## 2. PostgreSQL 실행 (1분)

```bash
# Docker로 PostgreSQL 실행
docker run -d \
  --name xperion-wiki-db \
  -e POSTGRES_DB=xperion_wiki \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15

# 실행 확인
docker ps | grep xperion-wiki-db
```

## 3. 데이터베이스 마이그레이션 (1분)

```bash
# 마이그레이션 적용
alembic upgrade head

# 성공 메시지 확인:
# INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial schema
# INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, Add tags table
```

## 4. 테스트 데이터 추가 (선택, 30초)

```bash
python scripts/seed_data.py

# 출력:
# 🌱 테스트 데이터 추가 중...
# ✅ 3개의 샘플 페이지가 추가되었습니다.
# ✅ 완료!
```

## 5. 서버 실행 (즉시)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 출력:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

## 6. API 테스트

### 브라우저에서

- **Swagger UI**: http://localhost:8000/docs
- **루트**: http://localhost:8000
- **헬스체크**: http://localhost:8000/health
- **페이지 목록**: http://localhost:8000/api/pages
- **검색**: http://localhost:8000/api/search?q=엘프

### curl로 테스트

```bash
# 헬스 체크
curl http://localhost:8000/health

# 페이지 목록
curl http://localhost:8000/api/pages

# 특정 페이지 조회
curl http://localhost:8000/api/pages/characters/player/elon

# 검색
curl "http://localhost:8000/api/search?q=팔라딘"

# 새 페이지 생성 (POST)
curl -X POST http://localhost:8000/api/pages \
  -H "Content-Type: application/json" \
  -d '{
    "title": "테스트 캐릭터",
    "slug": "test/character",
    "category": "characters/test",
    "content": "# 테스트 캐릭터\n\n테스트용 문서입니다.",
    "author": "Tester"
  }'
```

## 7. 구현된 API 목록

### Pages API (`/api/pages`)
- ✅ `GET /api/pages` - 문서 목록 (필터링, 정렬, 페이지네이션)
- ✅ `GET /api/pages/{slug}` - 문서 상세 조회
- ✅ `POST /api/pages` - 문서 생성 (GitHub 연동)
- ✅ `PUT /api/pages/{slug}` - 문서 수정 (동시성 제어)
- ✅ `DELETE /api/pages/{slug}` - 문서 삭제 (soft delete)

### Search API (`/api/search`)
- ✅ `GET /api/search?q={검색어}` - Trigram 기반 검색

### Tags API (`/api/tags`)
- ✅ `GET /api/tags` - 태그 목록

## 트러블슈팅

### 1. PostgreSQL 연결 오류

```bash
# PostgreSQL 컨테이너 상태 확인
docker logs xperion-wiki-db

# 재시작
docker restart xperion-wiki-db
```

### 2. GitHub API 오류

`.env`의 `GITHUB_TOKEN`과 `GITHUB_REPO` 확인:
```bash
# 토큰 테스트
curl -H "Authorization: token ghp_YOUR_TOKEN" \
  https://api.github.com/repos/username/xperion-wiki-content
```

### 3. 마이그레이션 오류

```bash
# 현재 버전 확인
alembic current

# 리셋 (주의: 모든 데이터 삭제)
alembic downgrade base
alembic upgrade head
```

### 4. 포트 충돌

```bash
# 다른 포트 사용
uvicorn app.main:app --reload --port 8001
```

## 다음 단계

백엔드가 정상 작동하면:

1. **프론트엔드 개발**: React + Vite로 UI 구축
2. **추가 기능**: 이미지 업로드, 실시간 검색, 통계
3. **배포**: Railway (백엔드) + Vercel (프론트엔드)

---

**문제가 발생하면** 에러 메시지를 공유해주세요!
