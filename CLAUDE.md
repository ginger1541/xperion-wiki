# Xperion Wiki - 개발 노트

## 현재 상태 (2026-01-17)

### 해결된 문제
1. **문서 클릭 시 랜딩 페이지로 리다이렉트** - 수정 완료
   - 원인: `doc.slug`가 `category/docSlug` 형태인데 상대 경로로 navigate하여 category 중복
   - 해결: WikiList.jsx, Dashboard.jsx에서 절대 경로 사용

2. **문서 상세 조회 500 에러** - 수정 완료
   - 원인: `db.refresh(page, ["tags"])` 후 tags relationship expired
   - 해결: raw SQL로 view_count 증가, page 객체 유지

### 미해결 문제
1. **GitHub Actions CI/CD 실패**
   - 증상: `ssh: unable to authenticate, attempted methods [none publickey]`
   - 원인: SSH 키 만료 후 새 키 등록했으나 appleboy/ssh-action에서 키 파싱 실패
   - 시도한 것:
     - ed25519 키 생성 및 등록 → 실패 (ssh: no key found)
     - RSA 4096 키 생성 → 아직 미등록
   - 임시 해결: 수동 SSH 배포

### 수동 배포 방법
```bash
# 로컬에서 SSH 접속
ssh -i ~/.ssh/gcp-xperion user@34.29.153.88

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
- 백엔드: `backend/app/api/pages.py` - Pages API
- CI/CD: `.github/workflows/deploy-backend.yml`

### SSH 키 정보
- 로컬 키 경로: `~/.ssh/gcp-xperion` (ed25519), `~/.ssh/gcp-xperion-rsa` (RSA)
- GCP 서버: 34.29.153.88, 사용자: user
- venv 경로: `/home/user/xperion-wiki/venv` (backend 폴더가 아닌 상위 폴더)
