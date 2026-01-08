# Xperion Wiki - Backend API

D&D TRPG 홈브류 서버를 위한 위키 시스템 백엔드 API

## 기술 스택

- **FastAPI**: 웹 프레임워크
- **PostgreSQL**: 데이터베이스
- **SQLAlchemy 2.0**: ORM (비동기)
- **Alembic**: 데이터베이스 마이그레이션
- **PyGithub**: GitHub API 연동

## 빠른 시작

### 1. 가상환경 생성 및 활성화

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env.example`을 `.env`로 복사하고 값을 수정:

```bash
cp .env.example .env
```

필수 환경 변수:
- `DATABASE_URL`: PostgreSQL 연결 문자열
- `GITHUB_TOKEN`: GitHub Personal Access Token
- `GITHUB_REPO`: GitHub 저장소 (예: username/xperion-wiki-content)
- `SECRET_KEY`: JWT 시크릿 키

### 4. PostgreSQL 실행 (Docker)

```bash
docker run -d \
  --name xperion-wiki-db \
  -e POSTGRES_DB=xperion_wiki \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15
```

### 5. 데이터베이스 마이그레이션

```bash
# 마이그레이션 초기화 (처음 한 번만)
alembic init alembic

# 마이그레이션 생성
alembic revision --autogenerate -m "Initial migration"

# 마이그레이션 적용
alembic upgrade head
```

### 6. 서버 실행

```bash
# 개발 서버 (자동 재시작)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는
python -m app.main
```

### 7. API 문서 확인

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 프로젝트 구조

```
backend/
├── app/
│   ├── api/           # API 라우터
│   ├── core/          # 핵심 설정 (config, security)
│   ├── db/            # 데이터베이스 설정
│   ├── models/        # SQLAlchemy 모델
│   ├── schemas/       # Pydantic 스키마
│   └── main.py        # FastAPI 앱
├── alembic/           # 데이터베이스 마이그레이션
├── tests/             # 테스트
├── .env.example       # 환경 변수 예제
├── requirements.txt   # Python 패키지
└── README.md
```

## 개발 가이드

### 새 API 엔드포인트 추가

1. `app/api/` 에 라우터 파일 생성
2. `app/main.py` 에 라우터 등록
3. 테스트 작성

### 데이터베이스 모델 추가

1. `app/models/` 에 모델 클래스 생성
2. Alembic 마이그레이션 생성 및 적용

### 테스트 실행

```bash
pytest
```

## 다음 단계

- [ ] Pages API 구현
- [ ] GitHub 연동
- [ ] 검색 기능
- [ ] 태그 시스템
- [ ] 이미지 업로드
