# Changelog

이 프로젝트의 주요 변경사항을 기록합니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)를 따르며,
버전 관리는 [Semantic Versioning](https://semver.org/lang/ko/)을 따릅니다.

---

## [Unreleased]

### 추가 예정
- 검색 페이지 UI
- 설정 페이지 UI
- 테스트 코드 확장
- 인증/권한 시스템
- 모니터링 및 로깅 개선

---

## [0.2.0] - 2026-01-16

### 추가됨 (Added)

#### 배포
- ✅ GCP Compute Engine 배포 완료 (e2-micro)
- ✅ Vercel 프론트엔드 배포 완료
- ✅ 프로덕션 환경 설정 완료
- ✅ GitHub 문서 저장소 분리 (xperion-wiki-content)

#### 데이터베이스
- Alembic 마이그레이션 003 추가 (`make_project_id_nullable`)
- `project_id` 컬럼을 nullable로 변경하여 유연성 향상

### 변경됨 (Changed)

#### 백엔드
- `PageBase` 스키마에서 `project_id`를 Optional로 변경
  - 프론트엔드가 `project_id` 없이도 문서 생성 가능
  - 더 유연한 문서 관리 구조

#### 프론트엔드
- WikiList: `project_id` 필터 제거하여 모든 문서 표시
- Dashboard: `project_id` 필터 제거하여 모든 문서 표시
- 검색 기능 개선: project_id 관계없이 전체 검색 가능

### 수정됨 (Fixed)

#### 배포 및 인프라
- **GitHub Token 권한 문제 해결**
  - Fine-grained Token의 Repository Access 설정 수정
  - `xperion-wiki-content` 레포지토리 접근 권한 추가
  - 403 Forbidden 에러 해결

- **문서 저장소 초기화**
  - `xperion-wiki-content` 레포지토리 생성 및 초기화
  - `content/` 폴더 구조 생성
  - README 및 가이드 문서 추가

- **데이터베이스 스키마 문제 해결**
  - `project_id` NOT NULL 제약조건으로 인한 500 에러 수정
  - 마이그레이션 체인 수정 (Multiple head revisions 에러 해결)
  - 003 마이그레이션의 `down_revision`을 '002'에서 'b8b586cd5b24'로 수정

- **검색 및 목록 표시 문제 해결**
  - `project_id=NULL`인 문서들이 필터링되어 보이지 않던 문제 수정
  - 프론트엔드에서 project_id 필터 제거
  - 모든 문서가 검색 결과 및 목록에 표시되도록 개선

#### API
- Vercel API 프록시 설정 수정 (중복 /api/ 경로 제거)
- MarkdownEditor disabled prop 버그 수정 (TDD 구현)

### 보안 (Security)
- 프로덕션 환경에서 GitHub Token 안전하게 설정
- GCP VM 환경변수 분리 및 보안 강화
- CORS 설정에 Vercel 배포 URL 추가

### 인프라 (Infrastructure)
- GCP VM 설정 및 최적화
  - PostgreSQL 설정
  - systemd 서비스 등록
  - 환경변수 관리
- Vercel 자동 배포 파이프라인 구축
- GitHub과 배포 서버 간 연동 완료

### 문서화 (Documentation)
- VERCEL_SETUP.md - Vercel 배포 가이드
- VERCEL_RECONNECT.md - Vercel GitHub 재연동 가이드
- CI_CD_SETUP.md - CI/CD 설정 가이드
- 트러블슈팅 문서 업데이트

---

## [0.1.0] - 2026-01-08

### 추가됨 (Added)

#### 백엔드
- FastAPI 프로젝트 초기화
- PostgreSQL 16 + SQLAlchemy 2.0 설정
- Alembic 데이터베이스 마이그레이션
- 5개 API 엔드포인트 구현
  - `GET /api/pages` - 문서 목록 조회
  - `GET /api/pages/{slug}` - 문서 상세 조회
  - `POST /api/pages` - 문서 생성
  - `PUT /api/pages/{slug}` - 문서 수정
  - `DELETE /api/pages/{slug}` - 문서 삭제
  - `GET /api/search` - 전문 검색
  - `GET /api/tags` - 태그 목록
  - `GET /api/tags/{tag}/pages` - 태그별 문서
  - `POST /api/upload/image` - 이미지 업로드
- PostgreSQL Trigram (pg_trgm) 한글 검색 구현
- GitHub API 연동 (PyGithub)
  - 자동 커밋
  - Frontmatter 생성
  - 파일 CRUD
- 태그 시스템
  - 계층적 태그 (`종족/엘프`)
  - 다대다 관계 (page_tags)
  - 사용 빈도 추적
- 동시성 제어 (낙관적 락, github_sha 기반)
- 구조화된 로깅 (structlog)
- API 문서화 (Swagger UI, ReDoc)
- 테스트 데이터 시드 스크립트

#### 프론트엔드
- React 19 + Vite 프로젝트 초기화
- React Router v7 라우팅 설정
- TailwindCSS Notion 스타일 디자인 시스템
- 4개 페이지 구현
  - ProjectSelector - 프로젝트 선택
  - Dashboard - 대시보드
  - WikiList - 문서 목록
  - WikiDetail - 문서 상세/편집
- 6개 컴포넌트 구현
  - AppLayout - 메인 레이아웃
  - Sidebar - 사이드바 네비게이션
  - Button - 버튼 컴포넌트 (4 variants)
  - Card - 카드 컴포넌트
  - MarkdownViewer - 마크다운 뷰어
  - MarkdownEditor - 분할 화면 에디터
- API 서비스 레이어 (`services/api.js`)
- 로딩/에러/빈 상태 UI
- 실시간 검색 필터
- 상대 시간 표시
- Slug 자동 생성

#### 데이터베이스
- 3개 테이블 스키마 설계
  - pages - 문서 메타데이터 및 캐시
  - tags - 태그
  - page_tags - 다대다 중간 테이블
- 인덱스 최적화
  - 기본 인덱스 (slug, category, status, updated_at)
  - Trigram GIN 인덱스 (title, content)
- 2개 마이그레이션
  - 001_initial_schema - Pages 테이블
  - 002_add_tags - Tags 테이블

#### 문서화
- DEVELOPMENT.md - 전체 아키텍처 및 설계 문서
- PROGRESS.md - 개발 진행상황
- DEPLOYMENT_GCP.md - GCP 배포 가이드
- README.md (루트, 백엔드, 프론트엔드)
- CHANGELOG.md (이 파일)

### 변경됨 (Changed)
- 없음 (초기 릴리스)

### 수정됨 (Fixed)

#### 백엔드
- psycopg2-binary 설치 문제 해결 (Python 3.13 호환)
- alembic.ini 한글 주석 인코딩 문제 해결
- seed_data.py UnicodeEncodeError 해결
- GitHub REPO 형식 수정 (URL → owner/repo)

#### 프론트엔드
- 없음 (초기 릴리스)

### 제거됨 (Removed)
- 없음 (초기 릴리스)

### 보안 (Security)
- GitHub Token 환경 변수 분리
- SECRET_KEY 환경 변수 분리
- CORS 설정 추가

---

## [0.0.1] - 2026-01-04

### 추가됨
- 프로젝트 초기화
- 기본 디렉토리 구조 생성
- .gitignore 설정

---

## 버전 관리 규칙

### 메이저 버전 (Major)
- 하위 호환성이 없는 API 변경
- 데이터베이스 스키마 주요 변경
- 아키텍처 대규모 변경

### 마이너 버전 (Minor)
- 하위 호환성이 있는 새 기능 추가
- API 엔드포인트 추가
- 새로운 페이지/컴포넌트 추가

### 패치 버전 (Patch)
- 버그 수정
- 성능 개선
- 문서 업데이트
- 리팩토링

---

## 릴리스 노트

### v0.1.0 - MVP 완성

이번 릴리스는 Xperion Wiki의 첫 번째 MVP (Minimum Viable Product) 버전입니다.

**주요 기능**:
- ✅ 마크다운 기반 문서 작성/편집
- ✅ PostgreSQL Trigram 한글 검색
- ✅ GitHub 자동 커밋
- ✅ 계층적 태그 시스템
- ✅ 관련 문서 추천
- ✅ 이미지 업로드

**기술적 성과**:
- FastAPI + SQLAlchemy 비동기 구조
- React 19 + Vite 최신 스택
- PostgreSQL Trigram을 활용한 고급 검색
- 낙관적 락을 통한 동시성 제어

**알려진 제한사항**:
- 인증/권한 시스템 미구현
- 테스트 코드 부재
- 프로덕션 배포 미완료

**다음 단계**:
- GCP 및 Vercel 배포
- 테스트 코드 작성
- 검색 페이지 UI 구현
- 모니터링 설정

---

[Unreleased]: https://github.com/ginger1541/xperion-wiki/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ginger1541/xperion-wiki/releases/tag/v0.1.0
[0.0.1]: https://github.com/ginger1541/xperion-wiki/releases/tag/v0.0.1
