# Xperion Wiki - 개발 노트

## 현재 상태 (2026-01-17)

### ✅ 해결된 문제

1. **문서 클릭 시 랜딩 페이지로 리다이렉트**
   - 원인: `doc.slug`가 `category/docSlug` 형태인데 상대 경로로 navigate하여 category 중복
   - 해결: WikiList.jsx, Dashboard.jsx에서 절대 경로 사용
   - 커밋: `bf38d2d`, `5127e86`

2. **문서 상세 조회 500 에러**
   - 원인: `db.refresh(page, ["tags"])` 후 tags relationship expired
   - 해결: raw SQL로 view_count 증가, page 객체 유지
   - 커밋: `193afa9`

3. **새 문서 저장 후 리다이렉트 오류**
   - 원인: `navigate("../${newPage.slug}")` → category 중복
   - 해결: 절대 경로 사용 `navigate("/project/${projectId}/wiki/${newPage.slug}")`
   - 커밋: `10e5ce0`

4. **+New 버튼 목업 상태**
   - 원인: onClick 핸들러 없음
   - 해결: 카테고리 선택 드롭다운 추가 (Character/Location/Lore)
   - 커밋: `bbbe94c`

### 🔄 CI/CD 상태 (검증 중)

- **문제**: SSH 키 만료 후 인증 실패
- **시도한 것**:
  - ed25519 키 → appleboy/ssh-action에서 파싱 실패
  - RSA 4096 키 → 테스트 중 (커밋: `f6cfeaf`)
- **로컬 SSH**: RSA 키로 접속 성공 확인됨
- **GitHub Actions**: 결과 대기 중

### 수동 배포 방법 (CI/CD 실패 시)
```bash
# 로컬에서 SSH 접속
ssh -i ~/.ssh/gcp-xperion-rsa user@34.29.153.88

# 서버에서 배포
cd /home/user/xperion-wiki
git pull origin main
source venv/bin/activate
cd backend
python -m alembic upgrade head
sudo systemctl restart xperion-wiki
```

### 주요 파일 경로
- 프론트엔드: `frontend/src/pages/`
  - WikiList.jsx - 문서 목록
  - WikiDetail.jsx - 문서 상세/편집
  - Dashboard.jsx - 대시보드
  - AppLayout.jsx - 레이아웃 (+New 버튼)
- 백엔드: `backend/app/api/pages.py` - Pages API
- CI/CD: `.github/workflows/deploy-backend.yml`

### SSH 키 정보
- 로컬 키 경로:
  - `~/.ssh/gcp-xperion` (ed25519) - 작동하지만 GitHub Actions 호환 문제
  - `~/.ssh/gcp-xperion-rsa` (RSA 4096) - 현재 사용 중
- GCP 서버: 34.29.153.88, 사용자: user
- venv 경로: `/home/user/xperion-wiki/venv` (상위 폴더)

### 프론트엔드 배포
- Vercel 자동 배포 (main 브랜치 push 시)
- vercel.json: `frontend/vercel.json`

### 백엔드 배포
- GitHub Actions → SSH → GCP VM
- 트리거: `backend/**` 또는 `.github/workflows/deploy-backend.yml` 변경 시
