# Vercel 기존 프로젝트 GitHub 재연동 가이드

**상황**: Vercel 프로젝트는 존재하지만 GitHub와 연동이 끊긴 경우

---

## 🔍 문제 확인

### 증상
- Vercel 프로젝트는 존재함
- GitHub에 푸시해도 자동 배포가 안 됨
- Vercel Dashboard에서 최신 커밋이 안 보임

### 원인
- Git Integration이 끊김
- 저장소 연결이 해제됨
- 권한 설정 문제

---

## ✅ 해결 방법 (3분)

### 방법 1: Git Integration 재연결 (추천)

#### Step 1: Vercel Dashboard 접속
1. https://vercel.com 로그인
2. **프로젝트 선택** (xperion-wiki)

#### Step 2: Settings로 이동
1. 프로젝트 페이지 상단의 **"Settings"** 탭 클릭

#### Step 3: Git 설정 확인
1. 좌측 메뉴에서 **"Git"** 선택
2. **"Connected Git Repository"** 섹션 확인

**연결되어 있으면**:
```
✅ Connected to ginger1541/xperion-wiki
Branch: main
```

**연결 안 되어 있으면**:
```
❌ No Git repository connected
또는
⚠️ Repository not found
```

#### Step 4-A: 연결이 끊긴 경우

**"Disconnect"** 버튼이 있다면:
1. **"Disconnect"** 클릭 (기존 연결 제거)
2. **"Connect Git Repository"** 버튼 클릭
3. **GitHub** 선택
4. `ginger1541/xperion-wiki` 저장소 선택
5. **"Connect"** 클릭

#### Step 4-B: 아예 연결이 없는 경우

1. **"Connect Git Repository"** 버튼 클릭
2. **GitHub** 선택
3. 저장소가 목록에 없으면:
   - **"Adjust GitHub App Permissions"** 클릭
   - Vercel에 저장소 접근 권한 부여
4. `ginger1541/xperion-wiki` 선택
5. **"Connect"** 클릭

#### Step 5: Root Directory 확인 (중요!)

**Settings** → **General** → **Root Directory**:
```
frontend
```

⚠️ **반드시 `frontend`로 설정되어 있어야 합니다!**

만약 비어있거나 다른 값이면:
1. **"Edit"** 클릭
2. `frontend` 입력
3. **"Save"** 클릭

#### Step 6: 환경 변수 확인

**Settings** → **Environment Variables**:
```
VITE_API_URL = http://34.29.153.88 (또는 실제 백엔드 IP)
```

없으면 추가:
1. **Name**: `VITE_API_URL`
2. **Value**: `http://YOUR_GCP_IP`
3. **"Add"** 클릭

#### Step 7: 수동 배포 트리거

**Deployments** 탭으로 이동:
1. 우측 상단 **"Create Deployment"** 버튼 클릭
2. **Branch**: `main` 선택
3. **"Deploy"** 클릭

또는 기존 배포에서:
1. 최근 배포 클릭
2. **⋯** 메뉴 → **"Redeploy"** 클릭

---

### 방법 2: 빠른 확인 (GitHub에서)

GitHub 저장소에서도 확인 가능:

1. https://github.com/ginger1541/xperion-wiki
2. **Settings** 탭
3. 좌측 메뉴 **"Integrations"** → **"GitHub Apps"**
4. **Vercel** 앱이 있는지 확인

**Vercel이 없으면**:
- Vercel과 GitHub 연동이 안 됨
- Vercel Dashboard에서 다시 연결 필요

**Vercel이 있으면**:
- 클릭해서 권한 확인
- `xperion-wiki` 저장소에 접근 권한이 있는지 확인

---

## 🧪 연동 테스트

### 테스트 1: 수동 배포

Vercel Dashboard → Deployments → Create Deployment

**성공**: 빌드가 시작되고 배포됨
**실패**: 에러 메시지 확인 (Root Directory, 환경 변수 등)

### 테스트 2: 자동 배포

간단한 변경 후 푸시:

```bash
# 테스트 파일 생성
cd frontend
echo "// Vercel auto-deploy test" >> src/main.jsx

git add .
git commit -m "test: verify Vercel auto-deploy"
git push origin main
```

**Vercel Dashboard → Deployments**에서:
- 새 배포가 자동으로 시작되면 ✅ 성공
- 아무 변화 없으면 ❌ 연동 안 됨

---

## 📊 현재 상태 확인 체크리스트

Vercel Dashboard에서 확인:

- [ ] **Settings → Git**: GitHub 저장소 연결됨
- [ ] **Settings → General → Root Directory**: `frontend`
- [ ] **Settings → Environment Variables**: `VITE_API_URL` 설정됨
- [ ] **Deployments**: 배포 이력 있음
- [ ] **테스트 푸시**: 자동 배포 작동

모두 체크되면 연동 완료! ✅

---

## 🐛 여전히 안 되면?

### 문제: Git 연결했는데도 자동 배포 안 됨

**확인 사항**:
1. **Production Branch 설정**
   - Settings → Git → Production Branch
   - `main`으로 설정되어 있는지 확인

2. **Ignored Build Step**
   - Settings → Git → Ignored Build Step
   - 커스텀 스크립트가 있으면 제거

3. **Deploy Hooks**
   - Settings → Git → Deploy Hooks
   - 불필요한 Hook 제거

### 문제: "Build Failed" 계속 발생

**로그 확인**:
1. 실패한 배포 클릭
2. 빌드 로그에서 에러 찾기

**일반적인 원인**:
```bash
# Root Directory 문제
Error: Cannot find module './frontend/package.json'
→ Root Directory를 'frontend'로 설정

# 환경 변수 문제
Error: VITE_API_URL is not defined
→ Environment Variables에 VITE_API_URL 추가

# 빌드 명령어 문제
Error: npm run build failed
→ 로컬에서 테스트: cd frontend && npm run build
```

---

## 🔄 최악의 경우: 프로젝트 재생성

모든 방법이 실패하면:

1. **기존 프로젝트 삭제** (주의!)
   - Settings → Advanced → Delete Project

2. **새 프로젝트 생성**
   - [VERCEL_SETUP.md](./VERCEL_SETUP.md) 가이드 따라하기

3. **커스텀 도메인 재설정** (있었다면)
   - Settings → Domains

---

## ✅ 연동 완료 후

### 배포 URL 확인
```
https://xperion-wiki.vercel.app
또는
https://[your-project].vercel.app
```

### 자동 배포 플로우
```
Git Push → GitHub → Vercel → 자동 빌드 → 배포 완료
```

이제 프론트엔드 코드를 푸시할 때마다 자동으로 배포됩니다! 🎉

---

**다음 단계**: CORS 설정 업데이트

백엔드(GCP)의 CORS 설정에 Vercel URL 추가:

```env
# GCP: /home/user/xperion-wiki/backend/.env
CORS_ORIGINS=https://xperion-wiki.vercel.app,http://localhost:5173
```

```bash
# GCP에서 백엔드 재시작
sudo systemctl restart xperion-wiki
```

---

**작성자**: Development Team
**최종 업데이트**: 2026-01-08
