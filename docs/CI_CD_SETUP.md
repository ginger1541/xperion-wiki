# CI/CD 설정 가이드

**작성일**: 2026-01-08
**버전**: 1.0.0

이 문서는 Xperion Wiki 프로젝트의 CI/CD 파이프라인을 설정하는 방법을 안내합니다.

---

## 📋 개요

현재 CI/CD 구성:
- **플랫폼**: GitHub Actions
- **워크플로우**: `.github/workflows/deploy-backend.yml`
- **트리거**: `main` 브랜치에 `backend/**` 또는 워크플로우 파일 변경 시
- **배포 대상**: GCP Compute Engine (e2-micro)

---

## 🔑 GitHub Secrets 설정

CI/CD가 작동하려면 다음 3개의 GitHub Secrets를 설정해야 합니다.

### 1. SSH 키 생성 (로컬 또는 GCP VM에서)

GCP VM에 접속하여 새로운 SSH 키를 생성합니다:

```bash
# GCP VM에 SSH 접속
ssh user@YOUR_GCP_IP

# SSH 키 생성 (비밀번호 없이)
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_key -N ""

# 공개 키를 authorized_keys에 추가
cat ~/.ssh/github_actions_key.pub >> ~/.ssh/authorized_keys

# 권한 설정
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/github_actions_key

# 비밀 키 내용 복사 (GitHub Secrets에 사용)
cat ~/.ssh/github_actions_key
```

**중요**: 생성된 비밀 키(`~/.ssh/github_actions_key`)의 전체 내용을 복사하세요. `-----BEGIN OPENSSH PRIVATE KEY-----`부터 `-----END OPENSSH PRIVATE KEY-----`까지 포함해야 합니다.

### 2. GitHub Repository에 Secrets 추가

1. GitHub 저장소 페이지로 이동
2. **Settings** > **Secrets and variables** > **Actions** 클릭
3. **New repository secret** 버튼 클릭

다음 3개의 Secrets를 추가:

#### `GCP_HOST`
```
YOUR_GCP_VM_IP_ADDRESS
```
예: `34.29.153.88`

#### `GCP_USERNAME`
```
user
```
GCP VM의 사용자 이름 (보통 `user` 또는 직접 설정한 이름)

#### `GCP_SSH_PRIVATE_KEY`
```
-----BEGIN OPENSSH PRIVATE KEY-----
(위에서 복사한 전체 비밀 키 내용 붙여넣기)
-----END OPENSSH PRIVATE KEY-----
```

**주의사항**:
- 비밀 키는 줄바꿈을 포함한 전체 내용을 복사해야 합니다
- 앞뒤 공백이 없어야 합니다
- BEGIN과 END 라인도 포함해야 합니다

---

## ✅ 설정 확인

### 1. GitHub Secrets 확인

Settings > Secrets and variables > Actions 페이지에서 다음 3개의 Secrets가 표시되어야 합니다:
- `GCP_HOST`
- `GCP_USERNAME`
- `GCP_SSH_PRIVATE_KEY`

### 2. SSH 연결 테스트 (로컬에서)

```bash
# 생성한 SSH 키로 GCP VM 접속 테스트
ssh -i ~/.ssh/github_actions_key user@YOUR_GCP_IP

# 성공하면 VM에 접속됨
```

### 3. 워크플로우 트리거 테스트

backend 디렉토리에 간단한 변경을 커밋하여 워크플로우를 트리거합니다:

```bash
# 테스트 커밋
cd backend
echo "# CI/CD test" >> README.md
git add README.md
git commit -m "test: trigger CI/CD workflow"
git push origin main
```

GitHub Actions 탭에서 워크플로우 실행 상태를 확인할 수 있습니다:
1. Repository > **Actions** 탭
2. 최근 워크플로우 실행 클릭
3. 로그 확인

---

## 🔧 워크플로우 동작 방식

`.github/workflows/deploy-backend.yml` 파일은 다음과 같이 작동합니다:

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'
```

**트리거 조건**:
- `main` 브랜치에 push
- `backend/` 디렉토리 또는 워크플로우 파일이 변경된 경우만

**배포 단계**:
1. GitHub Actions Runner가 SSH로 GCP VM에 접속
2. 최신 코드를 pull (`git pull origin main`)
3. 가상환경 활성화
4. 데이터베이스 마이그레이션 실행 (`alembic upgrade head`)
5. 백엔드 서비스 재시작 (`systemctl restart xperion-wiki`)

---

## 🚨 트러블슈팅

### 1. "Permission denied (publickey)" 오류

**원인**: SSH 키가 올바르게 설정되지 않음

**해결**:
- `GCP_SSH_PRIVATE_KEY` 시크릿이 전체 키 내용을 포함하는지 확인
- GCP VM의 `~/.ssh/authorized_keys`에 공개 키가 추가되었는지 확인
- SSH 키 파일 권한 확인: `chmod 600 ~/.ssh/authorized_keys`

### 2. "Host key verification failed" 오류

**원인**: GitHub Actions Runner가 GCP VM의 host key를 모름

**해결**: 워크플로우에 다음 옵션 추가 (이미 적용됨):
```yaml
- name: Deploy to GCP
  uses: appleboy/ssh-action@v1.0.3
  with:
    # ... 기존 설정 ...
    # 필요시 추가:
    # script_stop: true
```

### 3. "git pull" 권한 오류

**원인**: GCP VM에서 git repository 권한 문제

**해결**:
```bash
# GCP VM에서
cd /home/user/xperion-wiki
sudo chown -R user:user .
git config --global --add safe.directory /home/user/xperion-wiki
```

### 4. "systemctl restart" 권한 오류

**원인**: sudo 권한 필요

**해결**: GCP VM에서 사용자에게 sudo 권한 부여:
```bash
# root 또는 sudo 권한이 있는 사용자로
sudo visudo

# 다음 라인 추가 (user를 실제 사용자명으로 변경)
user ALL=(ALL) NOPASSWD: /bin/systemctl restart xperion-wiki
```

### 5. 워크플로우가 트리거되지 않음

**확인 사항**:
- `main` 브랜치에 push했는가?
- `backend/` 디렉토리 또는 워크플로우 파일을 변경했는가?
- GitHub Actions가 활성화되어 있는가? (Settings > Actions)

---

## 📊 모니터링

### GitHub Actions 로그 확인

1. Repository > **Actions** 탭
2. 워크플로우 실행 클릭
3. 각 단계별 로그 확인

### GCP VM 로그 확인

```bash
# SSH로 GCP VM 접속
ssh user@YOUR_GCP_IP

# 서비스 상태 확인
sudo systemctl status xperion-wiki

# 최근 로그 확인
sudo journalctl -u xperion-wiki -n 50 --no-pager

# 실시간 로그
sudo journalctl -u xperion-wiki -f
```

---

## 🔐 보안 고려사항

### 1. SSH 키 관리
- ✅ 배포 전용 SSH 키 사용 (개인 키와 분리)
- ✅ GitHub Secrets에 안전하게 저장
- ⚠️ 정기적으로 키 교체 (6개월마다 권장)

### 2. 최소 권한 원칙
- GCP VM 사용자는 필요한 최소 권한만 부여
- `sudo` 명령은 특정 명령으로 제한 (visudo 설정)

### 3. 네트워크 보안
- GCP VM의 SSH 포트를 특정 IP로 제한 가능
- 방화벽 규칙 설정 권장

---

## 📚 관련 문서

- [GCP 배포 가이드](./DEPLOYMENT_GCP.md)
- [개발 가이드](./DEVELOPMENT.md)
- [진행 상황](./PROGRESS.md)

---

## 📞 도움이 필요하신가요?

CI/CD 설정 중 문제가 발생하면:
1. GitHub Actions 로그 확인
2. GCP VM 서비스 로그 확인
3. 위 트러블슈팅 섹션 참고

**작성자**: Development Team
**최종 업데이트**: 2026-01-08
