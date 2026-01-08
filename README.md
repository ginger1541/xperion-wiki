# Xperion Wiki

> D&D 기반 홈브류 TRPG 서버를 위한 전용 위키 시스템

[![Status](https://img.shields.io/badge/status-MVP%20Complete-success)](https://github.com/ginger1541/xperion-wiki)
[![Backend](https://img.shields.io/badge/backend-FastAPI-009688)](./backend)
[![Frontend](https://img.shields.io/badge/frontend-React%2019-61DAFB)](./frontend)
[![Database](https://img.shields.io/badge/database-PostgreSQL%2016-336791)](https://www.postgresql.org/)

---

## 📖 프로젝트 개요

Xperion Wiki는 TRPG 세계관 설정을 체계적으로 관리하기 위한 웹 기반 위키 시스템입니다. 기존 구글 시트의 한계를 극복하고, 마크다운 기반의 자유로운 글쓰기 환경을 제공합니다.

### 핵심 기능

- 📝 **마크다운 에디터** - 실시간 미리보기, 문법 하이라이팅
- 🔍 **한글 전문 검색** - PostgreSQL Trigram 기반 고급 검색
- 🏷️ **계층적 태그** - 복잡한 설정을 체계적으로 분류
- 🔄 **GitHub 동기화** - Git 버전 관리 자동 연동
- 📊 **관련 문서 추천** - 태그 기반 자동 추천

---

## 🚀 빠른 시작

### 사전 요구사항

- **Python** 3.11+
- **Node.js** 18+
- **PostgreSQL** 16+
- **GitHub Personal Access Token** (Fine-grained)

### 1. 저장소 클론

```bash
git clone https://github.com/ginger1541/xperion-wiki.git
cd xperion-wiki
```

### 2. 백엔드 설정

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 실제 값 입력

# 데이터베이스 마이그레이션
alembic upgrade head

# (선택) 테스트 데이터 추가
python scripts/seed_data.py

# 서버 실행
uvicorn app.main:app --reload
```

백엔드가 http://localhost:8000 에서 실행됩니다.

### 3. 프론트엔드 설정

```bash
cd frontend

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 실제 값 입력

# 개발 서버 실행
npm run dev
```

프론트엔드가 http://localhost:5173 에서 실행됩니다.

### 4. 브라우저에서 확인

- **프론트엔드**: http://localhost:5173
- **백엔드 API 문서**: http://localhost:8000/docs

---

## 📂 프로젝트 구조

```
xperion-wiki/
├── backend/                # FastAPI 백엔드
│   ├── app/
│   │   ├── api/           # API 라우터
│   │   ├── models/        # 데이터베이스 모델
│   │   ├── schemas/       # Pydantic 스키마
│   │   ├── services/      # 비즈니스 로직
│   │   ├── db/            # 데이터베이스 설정
│   │   └── main.py        # FastAPI 앱
│   ├── alembic/           # 데이터베이스 마이그레이션
│   ├── scripts/           # 유틸리티 스크립트
│   └── requirements.txt
│
├── frontend/              # React 프론트엔드
│   ├── src/
│   │   ├── components/    # React 컴포넌트
│   │   ├── pages/         # 페이지 컴포넌트
│   │   ├── services/      # API 서비스
│   │   └── App.jsx
│   ├── public/
│   └── package.json
│
└── docs/                  # 프로젝트 문서
    ├── DEVELOPMENT.md     # 개발 가이드
    ├── PROGRESS.md        # 진행상황
    └── DEPLOYMENT_GCP.md  # 배포 가이드
```

---

## 🛠 기술 스택

### 백엔드
- **프레임워크**: FastAPI
- **ORM**: SQLAlchemy 2.0 (비동기)
- **데이터베이스**: PostgreSQL 16 + pg_trgm
- **마이그레이션**: Alembic
- **GitHub 연동**: PyGithub
- **로깅**: structlog

### 프론트엔드
- **프레임워크**: React 19
- **빌드 도구**: Vite 7
- **라우팅**: React Router v7
- **스타일링**: TailwindCSS
- **마크다운**: react-markdown + remark-gfm
- **HTTP 클라이언트**: Axios

### 인프라
- **백엔드 배포**: GCP Compute Engine (예정)
- **프론트엔드 배포**: Vercel (예정)
- **이미지 저장**: GitHub Repository
- **Markdown 저장**: GitHub Private Repository

---

## 📊 현재 상태

### Phase 1: MVP 개발 ✅ (완료)

**전체 진행률**: 85%

- ✅ **백엔드** (85%)
  - [x] 5개 API 엔드포인트 (pages, search, tags, upload, health)
  - [x] PostgreSQL Trigram 검색
  - [x] GitHub 자동 커밋
  - [x] 태그 시스템
  - [x] 동시성 제어

- ✅ **프론트엔드** (85%)
  - [x] 마크다운 에디터/뷰어
  - [x] 문서 CRUD
  - [x] 실시간 검색
  - [x] Notion 스타일 UI
  - [x] API 완전 연동

- ✅ **개발 환경** (100%)
  - [x] PostgreSQL 16 설정
  - [x] 백엔드 서버 실행
  - [x] 프론트엔드 서버 실행
  - [x] 통합 테스트 완료

**상세 진행상황**: [docs/PROGRESS.md](./docs/PROGRESS.md)

### 다음 단계: Phase 2 (배포 및 안정화)

- [ ] GCP Compute Engine 배포
- [ ] Vercel 배포
- [ ] CI/CD 파이프라인
- [ ] 모니터링 설정
- [ ] 테스트 코드 작성

---

## 📚 문서

- **[개발 문서](./docs/DEVELOPMENT.md)** - 전체 아키텍처, API 설계, 데이터 구조
- **[진행상황](./docs/PROGRESS.md)** - 현재 구현 상태 및 다음 단계
- **[GCP 배포 가이드](./docs/DEPLOYMENT_GCP.md)** - 프로덕션 배포 절차
- **[백엔드 README](./backend/README.md)** - 백엔드 상세 가이드
- **[프론트엔드 README](./frontend/README.md)** - 프론트엔드 상세 가이드

---

## 🔧 개발 가이드

### 백엔드 개발

```bash
cd backend

# 새 API 엔드포인트 추가
# 1. app/api/ 에 라우터 파일 생성
# 2. app/main.py 에 라우터 등록

# 데이터베이스 마이그레이션 생성
alembic revision -m "migration name"
alembic upgrade head

# 테스트 실행 (작성 예정)
pytest
```

### 프론트엔드 개발

```bash
cd frontend

# 새 페이지 추가
# 1. src/pages/ 에 컴포넌트 생성
# 2. src/App.jsx 에 라우트 추가

# 빌드
npm run build

# 린트
npm run lint
```

---

## 🐛 문제 해결

### 백엔드 서버가 시작되지 않을 때

1. PostgreSQL이 실행 중인지 확인
   ```bash
   # Windows
   sc query postgresql-x64-16

   # macOS
   brew services list | grep postgresql
   ```

2. 환경 변수 확인
   ```bash
   # .env 파일이 올바르게 설정되었는지 확인
   cat backend/.env
   ```

3. 데이터베이스 연결 테스트
   ```bash
   psql -U admin -d xperion_wiki -h localhost
   ```

### 프론트엔드가 백엔드와 통신하지 못할 때

1. CORS 설정 확인
   ```python
   # backend/app/main.py
   CORS_ORIGINS = ["http://localhost:5173"]
   ```

2. API URL 확인
   ```bash
   # frontend/.env
   VITE_API_URL=http://localhost:8000
   ```

---

## 🤝 기여하기

이 프로젝트는 현재 개인 프로젝트입니다. 기여를 원하시면 이슈를 열어주세요.

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

---

## 📞 연락처

- **GitHub**: [@ginger1541](https://github.com/ginger1541)
- **Repository**: [xperion-wiki](https://github.com/ginger1541/xperion-wiki)

---

## 🙏 감사의 글

- **FastAPI** - 현대적이고 빠른 Python 웹 프레임워크
- **React** - 유연한 UI 라이브러리
- **PostgreSQL** - 강력한 오픈소스 데이터베이스
- **TailwindCSS** - 유틸리티 우선 CSS 프레임워크

---

**마지막 업데이트**: 2026-01-08
