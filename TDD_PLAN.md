# CRUD Operations TDD Test Plan

## 테스트 목적
v0.2.0 배포 완료 후, 모든 CRUD 작업이 정상 동작하는지 검증

## 테스트 환경
- Backend: http://34.29.153.88/api
- Database: PostgreSQL (GCP VM)
- GitHub Integration: xperion-wiki-content repository

## 테스트 범위

### 1. CREATE (POST /api/pages)
**목표**: 새 문서 생성 기능 검증
- ✅ project_id 없이 문서 생성 가능 (nullable 확인)
- ✅ project_id 있는 문서 생성 가능
- ✅ GitHub에 자동 커밋되는지 확인
- ✅ 응답에 필수 필드 포함 확인 (id, slug, created_at 등)
- ✅ slug 자동 생성 확인

### 2. READ (GET /api/pages, GET /api/pages/{slug})
**목표**: 문서 조회 기능 검증
- ✅ 전체 문서 목록 조회 (project_id 필터 없이)
- ✅ 특정 slug로 문서 상세 조회
- ✅ project_id=NULL인 문서도 목록에 표시
- ✅ 카테고리 필터링 동작 확인
- ✅ 정렬 및 페이지네이션 확인

### 3. UPDATE (PUT /api/pages/{slug})
**목표**: 문서 수정 기능 검증
- ✅ 제목, 내용 수정 가능
- ✅ GitHub에 변경사항 자동 커밋
- ✅ updated_at 필드 업데이트 확인
- ✅ 동시성 제어 (github_sha 기반) 확인
- ✅ project_id 수정 가능 (NULL ↔ 값)

### 4. DELETE (DELETE /api/pages/{slug})
**목표**: 문서 삭제 기능 검증
- ✅ 문서 삭제 (status='deleted'로 변경)
- ✅ GitHub에서도 파일 삭제 확인
- ✅ 삭제된 문서는 목록에 미표시
- ✅ **모든 테스트 문서 정리** (사용자 요청)

## 테스트 데이터 전략
- CREATE: 3개의 테스트 문서 생성
  - `test-doc-1`: project_id=NULL, category=characters
  - `test-doc-2`: project_id="test-project", category=locations
  - `test-doc-3`: project_id=NULL, category=lore
- DELETE: 모든 테스트 문서 삭제 (slug에 'test-' 접두사 포함)

## 성공 기준
- [ ] 모든 CRUD 작업이 200/201 응답 반환
- [ ] GitHub 저장소에 변경사항 반영 확인
- [ ] 데이터베이스 상태 일관성 유지
- [ ] project_id nullable 동작 확인
- [ ] 테스트 후 정리 완료

## 실행 계획
1. pytest 테스트 파일 작성 (`backend/tests/test_crud_pages.py`)
2. 테스트 실행 및 결과 기록
3. 실패한 테스트 분석 및 수정
4. 최종 결과를 문서에 반영

---

**작성일**: 2026-01-17
**상태**: 진행 중
