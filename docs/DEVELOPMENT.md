# Xperion Wiki - 개발 문서

## 1. 프로젝트 개요

### 1.1 배경 및 목표
D&D 기반 홈브류 TRPG 서버를 위한 전용 위키 시스템 개발. 기존 구글 시트 기반 설정 관리의 한계를 극복하고, 글쓰기에 최적화된 플랫폼을 제공한다.

### 1.2 핵심 가치
- **글쓰기 중심**: 세계관, 설정, 캐릭터 등의 서사적 콘텐츠 작성에 최적화
- **구조화**: 태그 기반 분류 시스템으로 복잡한 설정을 체계적으로 관리
- **협업**: 서버 멤버 모두가 자유롭게 편집 가능
- **접근성**: 비개발자도 쉽게 사용할 수 있는 웹 기반 인터페이스

### 1.3 주요 사용자
- Dungeon Master (DM): 세계관 총괄 관리
- 플레이어: 캐릭터 설정, 스토리 기여
- 서버 멤버: 설정 참조 및 확장

---

## 2. 기술 스택 및 아키텍처

### 2.1 기술 스택

#### 프론트엔드
- **프레임워크**: React 18
- **빌드 도구**: Vite
- **라우팅**: React Router v6
- **스타일링**: TailwindCSS (또는 styled-components)
- **마크다운**: react-markdown, remark/rehype 플러그인
- **상태 관리**: React Context API (필요시 Zustand)
- **HTTP 클라이언트**: Axios

#### 백엔드
- **언어**: Python 3.11+
- **프레임워크**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **데이터 검증**: Pydantic v2
- **인증**: JWT (python-jose)
- **GitHub 연동**: PyGithub
- **로깅**: structlog
- **비동기**: asyncio, httpx

#### 데이터베이스
- **RDBMS**: PostgreSQL 15+
- **마이그레이션**: Alembic
- **용도**: 메타데이터, 통계, 사용자 세션, 검색 인덱스

#### 인프라 및 배포
- **프론트엔드 배포**: Vercel
- **백엔드 배포**: GCP Compute Engine e2-micro (Always Free)
- **데이터베이스**: PostgreSQL 15 (VM 자체 설치)
- **Markdown 저장소**: GitHub Private Repository
- **이미지 스토리지**: Cloudflare R2 (10GB 무료) 또는 GitHub Repository
- **웹 서버**: Nginx (리버스 프록시)
- **SSL 인증서**: Let's Encrypt (무료)
- **CI/CD**: GitHub Actions
- **모니터링**: Sentry (에러 트래킹) + 자체 로깅

### 2.2 시스템 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                     사용자                           │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│          프론트엔드 (React + Vite)                   │
│              Vercel/Netlify 배포                     │
│  - 위키 뷰어 (마크다운 렌더링)                        │
│  - 에디터 UI                                         │
│  - 검색 인터페이스                                    │
│  - 태그 필터링                                       │
└───────────────────┬─────────────────────────────────┘
                    │ HTTPS (REST API)
                    ▼
┌─────────────────────────────────────────────────────┐
│      GCP Compute Engine (e2-micro, Always Free)     │
│                                                      │
│  ┌─────────────────────────────────────────────┐  │
│  │  Nginx (리버스 프록시 + SSL)                  │  │
│  └─────────────────┬───────────────────────────┘  │
│                    ▼                                 │
│  ┌─────────────────────────────────────────────┐  │
│  │  FastAPI (Uvicorn)                          │  │
│  │  - /api/pages (CRUD)                        │  │
│  │  - /api/search                              │  │
│  │  - /api/tags                                │  │
│  │  - /api/upload (이미지)                     │  │
│  └─────────────────┬───────────────────────────┘  │
│                    ▼                                 │
│  ┌─────────────────────────────────────────────┐  │
│  │  PostgreSQL 15 (로컬 설치)                   │  │
│  │  - 검색 인덱스 (pg_trgm)                    │  │
│  │  - 메타데이터 캐시                           │  │
│  └─────────────────────────────────────────────┘  │
│                                                      │
└──────────────────────────┬──────────────────────────┘
                           │
                           ▼
                ┌─────────────────────────┐
                │  GitHub Repository      │
                │   (Private)             │
                │                         │
                │  /content/              │
                │    ├─ characters/       │
                │    ├─ locations/        │
                │    ├─ items/            │
                │    └─ lore/             │
                │  /images/               │
                │                         │
                │  ⚠️ Source of Truth      │
                └─────────────────────────┘
```

### 2.3 데이터 흐름

#### 문서 조회
```
사용자 → 프론트엔드 → 백엔드 API → PostgreSQL (content 캐시 + 메타데이터)
       ← 마크다운 원본 ←───────────┘

※ GitHub 호출 없음 (빠른 응답, API rate limit 절약)
```

#### 문서 편집/작성
```
사용자 → 웹 에디터 → 백엔드 API → 1. GitHub API (커밋) - Source of Truth
                                → 2. PostgreSQL (content + 메타데이터 캐싱)
                                → 3. 검색 인덱스 업데이트
                                → 4. 로그 기록
       ← 성공/실패 응답 ←──────────┘

※ 동기화: GitHub 커밋 성공 시 PostgreSQL 즉시 업데이트
```

#### 검색
```
사용자 → 검색어 입력 → 백엔드 API → PostgreSQL Trigram Search (content 대상)
       ← 검색 결과 + snippet ←───────┘

※ PostgreSQL에 content가 캐싱되어 있어 빠른 검색 (<100ms)
※ 제목/본문 가중치 기반 relevance 스코어링
```

---

## 3. 주요 기능 명세

### 3.1 필수 기능 (MVP)

#### 3.1.1 문서 관리
- **문서 조회**
  - 카테고리별 목록 (캐릭터, 지역, 아이템, 로어 등)
  - 개별 문서 상세 페이지
  - 마크다운 렌더링 (코드 하이라이팅, 테이블, 체크리스트 지원)
  - 목차(TOC) 자동 생성

- **문서 작성/편집**
  - 웹 기반 마크다운 에디터
  - 실시간 미리보기
  - Frontmatter 편집 (제목, 태그, 작성자, 날짜 등)
  - 자동 저장 (로컬 스토리지)

- **문서 삭제**
  - 소프트 삭제 (GitHub에서 archived 폴더로 이동)
  - 삭제 로그 기록

#### 3.1.2 태그 시스템
- **태그 분류**
  - 계층적 태그 (예: `종족/엘프`, `지역/북부/설산`)
  - 다중 태그 지원
  - 태그별 문서 목록

- **태그 필터링**
  - AND/OR 조건 검색
  - 태그 조합 (예: `종족:드워프 AND 지역:산맥`)

#### 3.1.3 검색 기능
- **전문 검색 (Full-Text Search)**
  - 제목, 본문 통합 검색
  - PostgreSQL `tsvector` 활용
  - 한글 형태소 분석 (필요시)

- **필터 옵션**
  - 카테고리별 필터
  - 작성자별 필터
  - 날짜 범위 필터

#### 3.1.4 이미지/파일 관리
- **이미지 업로드**
  - 드래그 앤 드롭
  - 자동 리사이징 (최대 2MB)
  - GitHub 저장소 또는 Cloudflare R2

- **이미지 첨부**
  - 마크다운 에디터에서 이미지 삽입
  - `![alt](url)` 자동 생성

### 3.2 부가 기능 (Post-MVP)

#### 3.2.1 버전 관리
- 문서 히스토리 (Git 커밋 기록 활용)
- 버전 비교 (diff)
- 특정 버전으로 롤백

#### 3.2.2 링크 시스템
- 위키 링크 (`[[문서명]]` → 자동 링크 생성)
- 역링크 (이 문서를 참조하는 다른 문서)
- 링크 유효성 검사

#### 3.2.3 통계 및 모니터링
- 문서별 조회수
- 인기 문서 랭킹
- 최근 수정 문서
- 편집 활동 그래프

#### 3.2.4 고급 검색
- 정규표현식 검색
- 유사 문서 추천
- 태그 자동 제안

---

## 4. 데이터 구조

### 4.1 Markdown 파일 구조

#### 디렉토리 구조
```
content/
├── characters/          # 캐릭터
│   ├── player/         # 플레이어 캐릭터
│   └── npc/            # NPC
├── locations/          # 지역
│   ├── cities/
│   ├── dungeons/
│   └── wilderness/
├── items/              # 아이템
│   ├── weapons/
│   ├── armor/
│   └── artifacts/
├── lore/               # 로어/설정
│   ├── history/
│   ├── factions/
│   └── religions/
└── sessions/           # 세션 기록
```

#### Frontmatter 형식
```yaml
---
title: "엘론 실버스트라이드"
category: "characters/player"
tags:
  - "종족/엘프"
  - "클래스/팔라딘"
  - "파티/실버문"
author: "PlayerName"
created: "2024-01-15"
updated: "2024-01-20"
status: "active"  # active, archived, draft
summary: "정의를 수호하는 엘프 팔라딘"
---

# 엘론 실버스트라이드

## 기본 정보
- **종족**: 하이엘프
- **클래스**: 팔라딘 (Oath of Devotion)
- **레벨**: 5

## 배경 스토리
...
```

### 4.2 데이터베이스 스키마

#### 4.2.1 pages (문서 메타데이터 및 캐시)
```sql
-- pg_trgm extension 활성화 (Trigram 검색용)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE pages (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(255) UNIQUE NOT NULL,  -- 파일 경로 (characters/player/elon.md)
    title VARCHAR(500) NOT NULL,
    category VARCHAR(100),
    author VARCHAR(100),

    -- 📄 컨텐츠 캐싱 (GitHub의 마크다운 원본을 PostgreSQL에 캐시)
    content TEXT NOT NULL,  -- 마크다운 원본 (검색 및 빠른 응답용)
    content_html TEXT,      -- 선택사항: 사전 렌더링된 HTML (성능 최적화)

    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'active',  -- active, archived, draft
    summary TEXT,

    -- 🔄 GitHub 동기화 메타데이터
    github_sha VARCHAR(40),   -- GitHub 파일 SHA (변경 감지, 중복 업데이트 방지)
    github_url TEXT,          -- GitHub 파일 URL (원본 소스 참조)
    last_synced_at TIMESTAMP, -- 마지막 동기화 시간

    view_count INTEGER DEFAULT 0,
    CONSTRAINT status_check CHECK (status IN ('active', 'archived', 'draft'))
);

-- 기본 인덱스
CREATE INDEX idx_pages_slug ON pages(slug);
CREATE INDEX idx_pages_category ON pages(category);
CREATE INDEX idx_pages_status ON pages(status);
CREATE INDEX idx_pages_updated ON pages(updated_at DESC);

-- 🔍 검색용 Trigram 인덱스 (한글 검색에 효과적)
CREATE INDEX idx_pages_title_trgm ON pages USING gin (title gin_trgm_ops);
CREATE INDEX idx_pages_content_trgm ON pages USING gin (content gin_trgm_ops);

-- 선택사항: Full-Text Search (tsvector) - Trigram보다 빠르지만 한글 지원 약함
-- CREATE INDEX idx_search_vector ON pages USING GIN(search_vector);
```

#### 4.2.2 tags (태그)
```sql
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,  -- 종족/엘프
    display_name VARCHAR(100),  -- 표시용 이름
    description TEXT,
    color VARCHAR(7),  -- 태그 색상 (#FF5733)
    usage_count INTEGER DEFAULT 0
);

CREATE INDEX idx_tags_name ON tags(name);
```

#### 4.2.3 page_tags (다대다 관계)
```sql
CREATE TABLE page_tags (
    page_id INTEGER REFERENCES pages(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (page_id, tag_id)
);

CREATE INDEX idx_page_tags_page ON page_tags(page_id);
CREATE INDEX idx_page_tags_tag ON page_tags(tag_id);
```

#### 4.2.4 edit_logs (편집 로그)
```sql
CREATE TABLE edit_logs (
    id SERIAL PRIMARY KEY,
    page_slug VARCHAR(255) NOT NULL,
    action VARCHAR(20) NOT NULL,  -- create, update, delete
    author VARCHAR(100),
    commit_sha VARCHAR(40),  -- GitHub 커밋 해시
    changes_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT action_check CHECK (action IN ('create', 'update', 'delete'))
);

CREATE INDEX idx_edit_logs_page ON edit_logs(page_slug);
CREATE INDEX idx_edit_logs_created ON edit_logs(created_at DESC);
```

#### 4.2.5 images (이미지 메타데이터)
```sql
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_name VARCHAR(255),
    url TEXT NOT NULL,  -- 실제 이미지 URL (GitHub 또는 R2)
    size_bytes INTEGER,
    mime_type VARCHAR(50),
    uploader VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    alt_text TEXT,
    used_in_pages TEXT[]  -- 이 이미지를 사용하는 문서 slug 배열
);

CREATE INDEX idx_images_filename ON images(filename);
```

#### 4.2.6 sync_queue (동기화 실패 복구용)
```sql
CREATE TABLE sync_queue (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(255) NOT NULL,
    github_sha VARCHAR(40) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, processing, completed, failed
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    error_message TEXT,
    CONSTRAINT status_check CHECK (status IN ('pending', 'processing', 'completed', 'failed'))
);

CREATE INDEX idx_sync_queue_status ON sync_queue(status);
CREATE INDEX idx_sync_queue_created ON sync_queue(created_at);
```

### 4.3 검색 구현 전략

검색은 이 위키 시스템의 핵심 기능입니다. TRPG 설정 문서는 복잡하게 얽혀있고, 효과적인 검색이 없으면 원하는 정보를 찾기 어렵습니다.

#### 4.3.1 한글 검색의 과제

**형태소 변화 문제:**
```
검색어: "팔라딘"
문서 내용: "팔라딘이", "팔라딘의", "팔라딘을", "팔라딘에게"
→ 정확한 매칭 어려움 (단순 LIKE 검색으로는 일부만 검색)
```

**해결 방법: PostgreSQL Trigram (pg_trgm)**
- Trigram: 3글자 단위로 문자열을 분해하여 유사도 계산
- 예: "팔라딘" → "팔라", "라딘"
- 한글 형태소 분석 없이도 효과적인 유사도 검색 가능

#### 4.3.2 검색 쿼리 구현

**기본 Trigram 검색:**
```sql
-- similarity() 함수: 0.0 ~ 1.0 유사도 반환
SELECT
    slug,
    title,
    content,
    similarity(title, '팔라딘') AS title_sim,
    similarity(content, '팔라딘') AS content_sim
FROM pages
WHERE
    title % '팔라딘'      -- % 연산자: 유사도 기반 매칭
    OR content % '팔라딘'
ORDER BY
    title_sim DESC,
    content_sim DESC
LIMIT 20;
```

**가중치 기반 검색 (제목 > 본문):**
```sql
SELECT
    *,
    (similarity(title, :query) * 3.0 +        -- 제목 가중치 3배
     similarity(content, :query) * 1.0) AS relevance_score
FROM pages
WHERE
    title % :query
    OR content % :query
ORDER BY relevance_score DESC
LIMIT 20;
```

**태그 포함 검색:**
```sql
SELECT
    p.*,
    (similarity(p.title, :query) * 3.0 +
     similarity(p.content, :query) * 1.0 +
     CASE WHEN EXISTS(
         SELECT 1 FROM page_tags pt
         JOIN tags t ON pt.tag_id = t.id
         WHERE pt.page_id = p.id
         AND t.name ILIKE '%' || :query || '%'
     ) THEN 2.0 ELSE 0.0 END) AS total_score
FROM pages p
WHERE
    p.title % :query
    OR p.content % :query
    OR EXISTS(
        SELECT 1 FROM page_tags pt
        JOIN tags t ON pt.tag_id = t.id
        WHERE pt.page_id = p.id AND t.name ILIKE '%' || :query || '%'
    )
ORDER BY total_score DESC
LIMIT 20;
```

**검색 결과 Snippet 생성:**
```sql
-- content에서 검색어 주변 텍스트 추출
SELECT
    slug,
    title,
    SUBSTRING(
        content
        FROM GREATEST(1, POSITION(:query IN content) - 50)
        FOR 150
    ) AS snippet
FROM pages
WHERE content % :query;
```

#### 4.3.3 검색 성능 최적화

**인덱스 활용:**
```sql
-- GIN 인덱스로 Trigram 검색 속도 향상 (10배 이상)
CREATE INDEX idx_pages_title_trgm ON pages USING gin (title gin_trgm_ops);
CREATE INDEX idx_pages_content_trgm ON pages USING gin (content gin_trgm_ops);

-- 유사도 임계값 설정 (기본 0.3)
SET pg_trgm.similarity_threshold = 0.2;  -- 더 많은 결과 반환
```

**성능 예상치:**
| 문서 수 | 인덱스 없음 | GIN 인덱스 사용 |
|---------|------------|----------------|
| 1,000개 | ~500ms | ~50ms |
| 10,000개 | ~5s | ~150ms |

#### 4.3.4 GitHub-PostgreSQL 동기화 전략

**원칙: GitHub = Source of Truth, PostgreSQL = Cache**

**문서 생성/수정 시 동기화:**
```python
# FastAPI 엔드포인트 예시
@app.put("/api/pages/{slug}")
async def update_page(slug: str, page_data: PageUpdate):
    # 1. GitHub에 커밋 (Source of Truth)
    github_result = await github_client.update_file(
        repo=GITHUB_REPO,
        path=f"content/{slug}.md",
        content=page_data.content,
        message=f"Update {page_data.title}",
        sha=page_data.github_sha  # 동시 수정 방지
    )

    # 2. PostgreSQL 캐시 업데이트
    await db.execute("""
        UPDATE pages
        SET
            content = :content,
            title = :title,
            updated_at = NOW(),
            github_sha = :new_sha,
            last_synced_at = NOW()
        WHERE slug = :slug
    """, {
        "content": page_data.content,
        "title": page_data.title,
        "new_sha": github_result.sha,
        "slug": slug
    })

    # 3. 로그 기록
    await log_edit(slug, "update", page_data.author, github_result.sha)

    return {"success": True, "commit_sha": github_result.sha}
```

**외부 편집 감지 (GitHub Actions):**
```yaml
# .github/workflows/sync-to-db.yml
name: Sync to PostgreSQL

on:
  push:
    paths:
      - 'content/**/*.md'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Trigger Backend Sync
        run: |
          # 변경된 파일 목록 추출
          FILES=$(git diff --name-only HEAD^ HEAD | grep '^content/.*\.md$')

          # 백엔드 API 호출하여 동기화
          for file in $FILES; do
            curl -X POST "${{ secrets.BACKEND_URL }}/api/sync/github" \
              -H "Authorization: Bearer ${{ secrets.SYNC_TOKEN }}" \
              -H "Content-Type: application/json" \
              -d "{\"file_path\": \"$file\"}"
          done
```

**백엔드 동기화 엔드포인트:**
```python
@app.post("/api/sync/github")
async def sync_from_github(sync_request: GitHubSyncRequest):
    # GitHub에서 파일 가져오기
    file_content = await github_client.get_file_content(
        repo=GITHUB_REPO,
        path=sync_request.file_path
    )

    # Frontmatter 파싱
    metadata, content = parse_frontmatter(file_content.decoded_content)

    # PostgreSQL 업데이트 (UPSERT)
    await db.execute("""
        INSERT INTO pages (slug, title, content, github_sha, ...)
        VALUES (:slug, :title, :content, :sha, ...)
        ON CONFLICT (slug)
        DO UPDATE SET
            content = EXCLUDED.content,
            github_sha = EXCLUDED.github_sha,
            last_synced_at = NOW()
    """, {...})

    return {"synced": True}
```

#### 4.3.5 검색 API 응답 예시

```json
{
  "query": "팔라딘",
  "total": 5,
  "search_time_ms": 87,
  "results": [
    {
      "slug": "characters/player/elon",
      "title": "엘론 실버스트라이드",
      "snippet": "...하이엘프 팔라딘으로, Oath of Devotion을 따르는...",
      "relevance_score": 0.92,
      "matched_in": ["title", "content"],
      "tags": ["종족/엘프", "클래스/팔라딘"],
      "category": "characters/player",
      "updated_at": "2024-01-20T15:30:00Z"
    },
    {
      "slug": "lore/factions/silver-hand",
      "title": "은빛 손 기사단",
      "snippet": "...팔라딘들로 구성된 기사단으로, 정의와 명예를...",
      "relevance_score": 0.75,
      "matched_in": ["content", "tags"],
      "tags": ["파벌/기사단", "클래스/팔라딘"],
      "category": "lore/factions",
      "updated_at": "2024-01-18T10:00:00Z"
    }
  ],
  "facets": {
    "categories": {
      "characters/player": 2,
      "lore/factions": 1,
      "items/weapons": 2
    },
    "tags": {
      "클래스/팔라딘": 5,
      "종족/엘프": 2
    }
  }
}
```

#### 4.3.6 고급 검색 기능 (Post-MVP)

**정규표현식 검색:**
```sql
SELECT * FROM pages
WHERE content ~ '드래곤.*고대'  -- "드래곤"과 "고대" 사이에 임의의 텍스트
```

**복합 필터 검색:**
```python
# 예: "종족이 엘프이고 클래스가 팔라딘인 캐릭터 검색"
query = {
    "text": "전설",
    "tags": ["종족/엘프", "클래스/팔라딘"],
    "category": "characters/player",
    "date_from": "2024-01-01"
}
```

**유사 문서 추천:**
```sql
-- 특정 문서와 유사한 다른 문서 찾기 (태그 기반)
SELECT p2.*, COUNT(*) as common_tags
FROM pages p1
JOIN page_tags pt1 ON p1.id = pt1.page_id
JOIN page_tags pt2 ON pt1.tag_id = pt2.tag_id
JOIN pages p2 ON pt2.page_id = p2.id
WHERE p1.slug = :current_slug AND p2.slug != :current_slug
GROUP BY p2.id
ORDER BY common_tags DESC
LIMIT 5;
```

### 4.4 동시성 처리 전략

여러 사용자가 동시에 같은 문서를 편집할 수 있는 환경에서의 충돌 처리 전략입니다. 복잡한 실시간 협업(OT, CRDT) 대신 **낙관적 락(Optimistic Locking)** 기반의 단순한 접근을 사용합니다.

#### 4.4.1 기본 원칙

```
복잡성 최소화: 실시간 동시 편집이 아닌, "먼저 저장한 사람이 승리" 모델
핵심: github_sha를 버전 식별자로 사용
```

#### 4.4.2 충돌 감지 흐름

```
1. 사용자 A, B가 동시에 "엘론" 문서 열기
   → 둘 다 github_sha: "abc123" 수신

2. A가 먼저 저장
   → GitHub 커밋 성공, 새 sha: "def456"
   → PostgreSQL 업데이트

3. B가 저장 시도 (여전히 sha: "abc123" 보유)
   → GitHub API 409 Conflict 반환
   → 백엔드에서 충돌 감지
```

#### 4.4.3 충돌 시 사용자 경험 (UX)

**API 응답:**
```json
{
  "error": {
    "code": "CONFLICT",
    "message": "다른 사용자가 이 문서를 수정했습니다",
    "details": {
      "your_sha": "abc123",
      "current_sha": "def456",
      "last_editor": "PlayerA",
      "last_edited_at": "2024-01-20T15:30:00Z"
    }
  },
  "current_content": "# 엘론 실버스트라이드\n\n(현재 저장된 내용...)"
}
```

**프론트엔드 처리:**
```javascript
// 충돌 발생 시 모달 표시
if (error.code === 'CONFLICT') {
  showConflictModal({
    yourContent: localContent,           // 사용자가 작성한 내용
    serverContent: error.current_content, // 서버의 최신 내용
    options: [
      { label: '내 변경사항으로 덮어쓰기', action: 'force_save' },
      { label: '서버 내용 가져오기 (내 작업 포기)', action: 'discard' },
      { label: '두 버전 비교하기', action: 'show_diff' }
    ]
  });
}
```

**간단한 Diff 표시 (선택사항):**
```
┌─────────────────────────────────────────┐
│  ⚠️ 문서 충돌 발생                        │
├─────────────────────────────────────────┤
│  PlayerA님이 3분 전에 이 문서를 수정했습니다  │
│                                         │
│  [내 버전]              [서버 버전]       │
│  레벨: 6               레벨: 5          │
│  HP: 45                HP: 42          │
│                                         │
│  [덮어쓰기]  [포기하고 새로고침]  [취소]   │
└─────────────────────────────────────────┘
```

#### 4.4.4 백엔드 구현

```python
@app.put("/api/pages/{slug}")
async def update_page(slug: str, page_data: PageUpdate):
    # 1. 현재 DB의 sha 확인
    current = await db.fetch_one(
        "SELECT github_sha FROM pages WHERE slug = :slug",
        {"slug": slug}
    )

    # 2. 클라이언트가 보낸 sha와 비교 (낙관적 락)
    if current and current.github_sha != page_data.expected_sha:
        # 충돌 감지 - 현재 내용과 함께 반환
        current_page = await get_page(slug)
        raise HTTPException(
            status_code=409,
            detail={
                "code": "CONFLICT",
                "message": "다른 사용자가 이 문서를 수정했습니다",
                "details": {
                    "your_sha": page_data.expected_sha,
                    "current_sha": current.github_sha,
                    "last_editor": current_page.author,
                    "last_edited_at": current_page.updated_at.isoformat()
                },
                "current_content": current_page.content
            }
        )

    # 3. 충돌 없음 - GitHub 커밋 진행
    try:
        github_result = await github_client.update_file(
            path=f"content/{slug}.md",
            content=page_data.content,
            sha=page_data.expected_sha  # GitHub도 sha 체크함
        )
    except GitHubConflictError:
        # GitHub에서도 충돌 감지 가능 (이중 안전장치)
        raise HTTPException(status_code=409, detail={"code": "CONFLICT", ...})

    # 4. PostgreSQL 업데이트
    await update_db_cache(slug, page_data, github_result.sha)

    return {"success": True, "new_sha": github_result.sha}
```

**강제 덮어쓰기 옵션:**
```python
@app.put("/api/pages/{slug}")
async def update_page(slug: str, page_data: PageUpdate):
    # force=True면 sha 체크 건너뛰기
    if not page_data.force:
        # ... 위의 충돌 체크 로직
        pass

    # force=True인 경우
    # 현재 GitHub의 최신 sha를 가져와서 사용
    current_file = await github_client.get_file(f"content/{slug}.md")
    github_result = await github_client.update_file(
        path=f"content/{slug}.md",
        content=page_data.content,
        sha=current_file.sha  # 최신 sha로 덮어쓰기
    )
```

#### 4.4.5 편집 중 알림 (선택사항, Post-MVP)

복잡한 실시간 동기화 없이 간단한 폴링으로 구현:

```javascript
// 편집 화면에서 30초마다 체크
const checkForUpdates = async () => {
  const response = await fetch(`/api/pages/${slug}/check?sha=${currentSha}`);
  if (response.data.has_update) {
    showWarning('다른 사용자가 이 문서를 수정했습니다. 저장 전 확인하세요.');
  }
};

setInterval(checkForUpdates, 30000);
```

```python
@app.get("/api/pages/{slug}/check")
async def check_update(slug: str, sha: str):
    current = await db.fetch_one(
        "SELECT github_sha FROM pages WHERE slug = :slug",
        {"slug": slug}
    )
    return {"has_update": current.github_sha != sha}
```

### 4.5 에러 처리 및 복구 전략

GitHub과 PostgreSQL 두 저장소 간의 일관성을 유지하기 위한 에러 처리 전략입니다. 복잡한 분산 트랜잭션 대신 **최종 일관성(Eventual Consistency)** 모델을 사용합니다.

#### 4.5.1 기본 원칙

```
1. GitHub = Source of Truth (절대적 원본)
2. PostgreSQL = Cache (복구 가능한 캐시)
3. GitHub 실패 → 전체 실패 (롤백)
4. PostgreSQL 실패 → 재시도 + 백그라운드 복구
```

#### 4.5.2 에러 시나리오별 처리

**시나리오 1: GitHub 커밋 실패**
```python
async def update_page(slug: str, page_data: PageUpdate):
    try:
        github_result = await github_client.update_file(...)
    except GitHubAPIError as e:
        # GitHub 실패 = 전체 실패
        # PostgreSQL에 아무것도 하지 않음
        logger.error("github_commit_failed", slug=slug, error=str(e))
        raise HTTPException(
            status_code=502,
            detail={
                "code": "GITHUB_ERROR",
                "message": "저장에 실패했습니다. 잠시 후 다시 시도해주세요.",
                "retry_after": 5
            }
        )
```

**시나리오 2: GitHub 성공, PostgreSQL 실패**
```python
async def update_page(slug: str, page_data: PageUpdate):
    # 1. GitHub 커밋 성공
    github_result = await github_client.update_file(...)

    # 2. PostgreSQL 업데이트 시도 (재시도 로직 포함)
    try:
        await update_db_with_retry(slug, page_data, github_result.sha)
    except DatabaseError as e:
        # DB 실패해도 사용자에겐 성공 반환
        # 백그라운드에서 복구 예약
        logger.error("db_update_failed",
            slug=slug,
            github_sha=github_result.sha,
            error=str(e)
        )
        await schedule_sync_retry(slug, github_result.sha)

        # 사용자에겐 성공으로 응답 (GitHub에는 저장됨)
        return {
            "success": True,
            "new_sha": github_result.sha,
            "warning": "저장되었습니다. 검색 반영에 시간이 걸릴 수 있습니다."
        }

async def update_db_with_retry(slug, page_data, sha, max_retries=3):
    """즉시 재시도 (지수 백오프)"""
    for attempt in range(max_retries):
        try:
            await db.execute(...)
            return
        except DatabaseError:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 1, 2, 4초
            else:
                raise
```

#### 4.5.3 불일치 감지 및 복구

**sync_queue 테이블:**
```sql
CREATE TABLE sync_queue (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(255) NOT NULL,
    github_sha VARCHAR(40) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, processing, completed, failed
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    error_message TEXT
);

CREATE INDEX idx_sync_queue_status ON sync_queue(status);
```

**백그라운드 동기화 워커:**
```python
# 별도 프로세스 또는 스케줄러에서 실행
async def sync_worker():
    """1분마다 실행되는 동기화 워커"""
    while True:
        # 1. 실패한 동기화 작업 가져오기
        pending = await db.fetch_all("""
            SELECT * FROM sync_queue
            WHERE status IN ('pending', 'failed')
            AND retry_count < 5
            ORDER BY created_at ASC
            LIMIT 10
        """)

        for item in pending:
            try:
                # GitHub에서 최신 내용 가져오기
                content = await github_client.get_file_content(
                    f"content/{item.slug}.md"
                )

                # PostgreSQL 업데이트
                await sync_page_to_db(item.slug, content, item.github_sha)

                # 큐에서 완료 처리
                await db.execute("""
                    UPDATE sync_queue
                    SET status = 'completed', processed_at = NOW()
                    WHERE id = :id
                """, {"id": item.id})

                logger.info("sync_recovered", slug=item.slug)

            except Exception as e:
                await db.execute("""
                    UPDATE sync_queue
                    SET status = 'failed',
                        retry_count = retry_count + 1,
                        error_message = :error
                    WHERE id = :id
                """, {"id": item.id, "error": str(e)})

        await asyncio.sleep(60)  # 1분 대기
```

#### 4.5.4 일관성 검증 (선택사항)

```python
@app.post("/api/admin/verify-consistency")
async def verify_consistency():
    """관리자용: GitHub와 PostgreSQL 일관성 검증"""

    # GitHub의 모든 파일 목록
    github_files = await github_client.get_tree("content/")

    # PostgreSQL의 모든 문서
    db_pages = await db.fetch_all("SELECT slug, github_sha FROM pages")
    db_map = {p.slug: p.github_sha for p in db_pages}

    inconsistencies = []

    for file in github_files:
        slug = file.path.replace("content/", "").replace(".md", "")

        if slug not in db_map:
            inconsistencies.append({
                "slug": slug,
                "issue": "missing_in_db",
                "github_sha": file.sha
            })
        elif db_map[slug] != file.sha:
            inconsistencies.append({
                "slug": slug,
                "issue": "sha_mismatch",
                "github_sha": file.sha,
                "db_sha": db_map[slug]
            })

    return {
        "total_github": len(github_files),
        "total_db": len(db_pages),
        "inconsistencies": inconsistencies
    }

@app.post("/api/admin/force-sync")
async def force_sync(slug: str = None):
    """강제 동기화 (전체 또는 특정 문서)"""
    if slug:
        await sync_single_page(slug)
    else:
        await sync_all_pages()  # 전체 재동기화
    return {"success": True}
```

#### 4.5.5 사용자 에러 메시지 가이드

| 에러 코드 | 상황 | 사용자 메시지 | 액션 |
|----------|------|-------------|------|
| `GITHUB_ERROR` | GitHub API 장애 | "저장에 실패했습니다. 잠시 후 다시 시도해주세요." | 재시도 버튼 |
| `CONFLICT` | 동시 편집 충돌 | "다른 사용자가 이 문서를 수정했습니다." | 덮어쓰기/새로고침 선택 |
| `VALIDATION_ERROR` | 입력값 오류 | "제목은 필수입니다." | 입력 필드 하이라이트 |
| `DB_SYNC_DELAYED` | DB 동기화 지연 | "저장되었습니다. 검색 반영에 시간이 걸릴 수 있습니다." | 정보성 알림 |
| `RATE_LIMITED` | 요청 과다 | "요청이 너무 많습니다. 잠시 후 다시 시도해주세요." | 대기 후 재시도 |

#### 4.5.6 에러 흐름 요약

```
┌─────────────────────────────────────────────────────────┐
│                    문서 저장 요청                         │
└─────────────────────────┬───────────────────────────────┘
                          ▼
                ┌─────────────────┐
                │  충돌 체크       │
                │  (sha 비교)      │
                └────────┬────────┘
                         │
           ┌─────────────┴─────────────┐
           ▼                           ▼
    [충돌 없음]                    [충돌 발생]
           │                           │
           ▼                           ▼
    ┌─────────────┐              409 CONFLICT
    │ GitHub 커밋  │              (두 버전 반환)
    └──────┬──────┘
           │
     ┌─────┴─────┐
     ▼           ▼
 [성공]       [실패]
     │           │
     ▼           ▼
┌─────────┐   502 GITHUB_ERROR
│ DB 저장  │   (재시도 안내)
└────┬────┘
     │
  ┌──┴──┐
  ▼     ▼
[성공] [실패]
  │     │
  ▼     ▼
200 OK  200 OK + warning
        + sync_queue에 추가
        + 백그라운드 복구
```

---

## 5. API 설계

### 5.1 API 엔드포인트

#### 5.1.1 문서 관리

**GET /api/pages**
- 설명: 문서 목록 조회
- 쿼리 파라미터:
  - `category`: 카테고리 필터
  - `tag`: 태그 필터 (콤마 구분 다중 가능)
  - `status`: active/archived/draft
  - `sort`: created_at, updated_at, title, view_count
  - `order`: asc/desc
  - `page`, `limit`: 페이지네이션
- 응답:
```json
{
  "total": 45,
  "pages": [
    {
      "slug": "characters/player/elon",
      "title": "엘론 실버스트라이드",
      "category": "characters/player",
      "tags": ["종족/엘프", "클래스/팔라딘"],
      "author": "PlayerName",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-20T15:30:00Z",
      "summary": "정의를 수호하는 엘프 팔라딘",
      "view_count": 42
    }
  ]
}
```

**GET /api/pages/{slug}**
- 설명: 문서 상세 조회
- 응답:
```json
{
  "slug": "characters/player/elon",
  "title": "엘론 실버스트라이드",
  "category": "characters/player",
  "tags": ["종족/엘프", "클래스/팔라딘"],
  "author": "PlayerName",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-20T15:30:00Z",
  "content": "# 엘론 실버스트라이드\n\n## 기본 정보...",
  "view_count": 42,
  "related_pages": [...]  // 같은 태그를 가진 문서들
}
```

**POST /api/pages**
- 설명: 새 문서 생성
- 요청 본문:
```json
{
  "title": "새 캐릭터",
  "category": "characters/npc",
  "tags": ["종족/인간", "직업/상인"],
  "content": "# 새 캐릭터\n\n...",
  "author": "DMName"
}
```
- 응답: 생성된 문서 정보 + GitHub 커밋 해시

**PUT /api/pages/{slug}**
- 설명: 문서 수정
- 요청 본문: POST와 동일
- 응답: 업데이트된 문서 정보

**DELETE /api/pages/{slug}**
- 설명: 문서 삭제 (soft delete)
- 응답: 삭제 로그 정보

#### 5.1.2 검색

**GET /api/search**
- 쿼리 파라미터:
  - `q`: 검색어
  - `category`: 카테고리 필터
  - `tags`: 태그 필터
  - `page`, `limit`
- 응답:
```json
{
  "total": 12,
  "results": [
    {
      "slug": "...",
      "title": "...",
      "snippet": "...검색어가 포함된 본문 일부...",
      "relevance": 0.85
    }
  ]
}
```

#### 5.1.3 태그

**GET /api/tags**
- 설명: 전체 태그 목록 (사용 빈도 포함)
- 응답:
```json
{
  "tags": [
    {
      "name": "종족/엘프",
      "display_name": "엘프",
      "color": "#4CAF50",
      "usage_count": 15
    }
  ]
}
```

**GET /api/tags/{tag_name}/pages**
- 설명: 특정 태그의 문서 목록

#### 5.1.4 이미지 업로드

**POST /api/upload/image**
- 설명: 이미지 업로드
- 요청: multipart/form-data
- 응답:
```json
{
  "url": "https://raw.githubusercontent.com/.../image.png",
  "filename": "image.png",
  "size": 245678
}
```

#### 5.1.5 통계

**GET /api/stats/recent**
- 설명: 최근 수정된 문서 목록

**GET /api/stats/popular**
- 설명: 인기 문서 (조회수 기준)

**GET /api/logs**
- 설명: 편집 로그 (관리자용)

### 5.2 에러 처리

```json
{
  "error": {
    "code": "PAGE_NOT_FOUND",
    "message": "문서를 찾을 수 없습니다",
    "details": {}
  }
}
```

주요 에러 코드:
- `PAGE_NOT_FOUND`: 404
- `VALIDATION_ERROR`: 400
- `GITHUB_API_ERROR`: 502
- `INTERNAL_ERROR`: 500

---

## 6. 배포 전략

### 6.1 개발 환경

#### 로컬 개발
```bash
# 프론트엔드
cd frontend
npm install
npm run dev  # localhost:5173

# 백엔드
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload  # localhost:8000

# PostgreSQL (Docker)
docker run -d \
  --name xperion-wiki-db \
  -e POSTGRES_DB=xperion_wiki \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15
```

#### 환경 변수
```env
# backend/.env
DATABASE_URL=postgresql://admin:password@localhost:5432/xperion_wiki
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
GITHUB_REPO=username/xperion-wiki-content
GITHUB_BRANCH=main
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:5173

# frontend/.env
VITE_API_URL=http://localhost:8000
```

### 6.2 프로덕션 배포

#### GCP Compute Engine 배포 (백엔드)

**완전한 배포 가이드는 `/docs/DEPLOYMENT_GCP.md`를 참조하세요.**

**요약:**
1. GCP Console에서 e2-micro VM 생성 (us-central1 리전)
2. Ubuntu 22.04 LTS 설치
3. SSH 접속 후 배포 스크립트 실행:
   ```bash
   cd ~/xperion-wiki/backend/scripts/deploy/gcp
   bash 01-setup-vm.sh          # VM 초기 설정
   bash 02-setup-database.sh    # PostgreSQL 설정
   bash 03-deploy-app.sh        # 애플리케이션 배포
   bash 04-setup-nginx.sh       # Nginx + SSL 설정
   ```

4. 환경 변수 (.env 파일):
   - `DATABASE_URL` (로컬 PostgreSQL)
   - `GITHUB_TOKEN` (Fine-grained PAT)
   - `GITHUB_REPO`
   - `SECRET_KEY`
   - `CORS_ORIGINS` (Vercel 프론트엔드 URL)

5. systemd 서비스로 자동 시작

**비용:** 완전 무료 (Always Free 티어)

#### Vercel 배포 (프론트엔드)
1. Vercel 프로젝트 연결 (GitHub)
2. 환경 변수 설정:
   - `VITE_API_URL` (GCP VM 백엔드 URL, 예: https://api.xperion-wiki.com)
3. 빌드 설정:
   - Build Command: `npm run build`
   - Output Directory: `dist`

### 6.3 GitHub Actions CI/CD

```yaml
# .github/workflows/backend-deploy.yml
name: Deploy Backend to GCP

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          cd backend
          pip install -r requirements.txt
          pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to GCP VM
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.GCP_VM_IP }}
          username: ${{ secrets.GCP_VM_USER }}
          key: ${{ secrets.GCP_SSH_KEY }}
          script: |
            cd ~/xperion-wiki/backend/scripts/deploy/gcp
            bash update-app.sh
```

---

## 7. 모니터링 및 로깅

### 7.1 로깅 전략

#### 백엔드 로깅 (structlog)
```python
import structlog

logger = structlog.get_logger()

# API 요청 로깅
logger.info("page_viewed",
    slug=page_slug,
    user=user_id,
    duration_ms=125)

# 에러 로깅
logger.error("github_api_error",
    endpoint="/contents/...",
    status_code=403,
    error=str(e))
```

#### 로그 레벨
- **INFO**: 일반 요청, 성공적인 작업
- **WARNING**: GitHub API rate limit 근접, 느린 쿼리
- **ERROR**: API 실패, DB 에러
- **CRITICAL**: 서비스 장애

### 7.2 메트릭 수집

#### 시스템 메트릭 (GCP VM)
- CPU 사용률: `htop`, `top`
- 메모리 사용률: `free -h`
- 디스크 사용량: `df -h`
- 네트워크 트래픽: `iftop`
- 서비스 상태: `systemctl status xperion-wiki`

#### 커스텀 메트릭 (DB 저장)
```sql
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(50),
    value FLOAT,
    labels JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 예시: API 응답 시간
INSERT INTO metrics (metric_name, value, labels)
VALUES ('api_response_time', 125.5, '{"endpoint": "/api/pages", "method": "GET"}');
```

### 7.3 에러 트래킹 (Sentry)

#### 프론트엔드
```javascript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "https://...@sentry.io/...",
  environment: import.meta.env.MODE,
  tracesSampleRate: 1.0,
});
```

#### 백엔드
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://...@sentry.io/...",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

### 7.4 알림 설정

#### 시스템 알림 (선택사항)
- 디스크 사용량 80% 초과 시 이메일 알림 (cron + script)
- 서비스 다운 시 재시작 (systemd Restart=always)
- 메모리 부족 시 자동 재시작 (systemd MemoryMax)

#### Sentry 알림
- 에러 발생 시 즉시 알림
- 에러 빈도 급증 시 알림

#### GitHub Actions 알림
- 배포 실패 시 이메일 알림
- 테스트 실패 시 알림

---

## 8. 개발 로드맵

### Phase 1: MVP 개발 ✅ (완료 - 2026-01-08)

#### Week 1-2: 백엔드 기반 구축 ✅
- [x] FastAPI 프로젝트 초기화
- [x] PostgreSQL 스키마 설계 및 마이그레이션
- [x] GitHub API 연동 (파일 읽기/쓰기)
- [x] 기본 CRUD API 구현
- [ ] GCP Compute Engine 배포 환경 구축 (진행 중)

#### Week 3-4: 프론트엔드 기본 구조 ✅
- [x] React + Vite 프로젝트 초기화
- [x] 라우팅 설정 (문서 목록/상세)
- [x] 마크다운 렌더러 구현
- [x] 기본 UI/UX (TailwindCSS)
- [ ] Vercel 배포 (진행 예정)

#### Week 5-6: 핵심 기능 구현 ✅
- [x] 마크다운 에디터 (실시간 미리보기)
- [x] 태그 시스템
- [x] 전문 검색 (PostgreSQL Trigram)
- [x] 이미지 업로드
- [x] 통합 테스트

**진행률**: 85% (배포 제외 시 완료)
**상세 진행상황**: [PROGRESS.md](./PROGRESS.md) 참조

### Phase 2: 고도화 (4주)

#### Week 7-8: 사용성 개선
- [ ] 위키 링크 시스템 (`[[문서명]]`)
- [ ] 역링크 표시
- [ ] 문서 버전 히스토리
- [ ] 자동 저장 기능

#### Week 9-10: 모니터링 및 최적화
- [ ] 로깅 시스템 강화
- [ ] Sentry 에러 트래킹
- [ ] 성능 최적화 (쿼리, 인덱스)
- [ ] 캐싱 전략 (Redis 선택적 도입)

### Phase 3: 확장 기능 (진행형)
- [ ] 통계 대시보드
- [ ] 문서 템플릿 시스템
- [ ] 고급 검색 (정규표현식, 필터)
- [ ] 모바일 앱 (선택사항)
- [ ] API 문서 자동 생성 (OpenAPI)

---

## 9. 참고 사항

### 9.1 비용 예상

- **GCP Compute Engine**: **무료** (e2-micro, Always Free 티어)
  - 720시간/월 (24/7 가능)
  - 30GB 표준 디스크
  - 1GB 아웃바운드 트래픽/월
  - ⚠️ 트래픽 초과 시: $0.12/GB (10GB 초과해도 $1.2)
- **PostgreSQL**: **무료** (VM 자체 설치)
- **Nginx + SSL**: **무료** (오픈소스 + Let's Encrypt)
- **Vercel**: **무료** (Hobby 플랜, 100GB 대역폭)
- **GitHub**: **무료** (Private repo, 1GB 스토리지)
- **Cloudflare R2**: **무료** (10GB 스토리지)
- **Sentry**: **무료** (5,000 이벤트/월)

**총 예상 비용: $0/월** (완전 무료!)
**최대 비용 (트래픽 초과 시): ~$1-2/월**

### 9.2 성능 목표

- **페이지 로딩**: < 1초 (프론트엔드)
- **API 응답**: < 200ms (평균)
- **검색 응답**: < 500ms
- **문서 저장**: < 3초 (GitHub 커밋 포함)

### 9.3 확장성 고려사항

- **문서 수**: 최대 10,000개 (PostgreSQL FTS 충분)
- **동시 사용자**: 50명 (Railway 무료 티어 충분)
- **이미지 스토리지**: 10GB (Cloudflare R2 무료 한도)

---

## 10. 다음 단계

1. **GitHub Repository 생성**
   - `xperion-wiki` (메인 프로젝트)
   - `xperion-wiki-content` (Private, Markdown 파일)

2. **개발 환경 세팅**
   - 로컬 PostgreSQL 설치
   - GitHub Token 발급 (Fine-grained PAT)

3. **GCP VM 생성 및 배포**
   - **상세 가이드**: [`/docs/DEPLOYMENT_GCP.md`](/docs/DEPLOYMENT_GCP.md)
   - GCP Console에서 e2-micro VM 생성
   - 배포 스크립트 실행

4. **프로토타입 개발 시작**
   - 백엔드: 간단한 페이지 CRUD
   - 프론트엔드: 문서 조회 화면

---

## 관련 문서

- **[GCP 배포 가이드](/docs/DEPLOYMENT_GCP.md)**: 완전한 배포 절차 및 트러블슈팅
- **[배포 스크립트 README](/backend/scripts/deploy/gcp/README.md)**: 스크립트 사용법

---

**문서 작성일**: 2026-01-04
**최종 수정일**: 2026-01-07
**작성자**: AI Assistant + 프로젝트 오너
