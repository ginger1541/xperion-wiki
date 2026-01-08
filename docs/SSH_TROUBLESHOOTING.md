# SSH 인증 오류 해결 가이드

**오류**: `ssh: unable to authenticate, attempted methods [none publickey], no supported methods remain`

이 오류는 GitHub Actions가 GCP VM에 SSH 인증을 하지 못한다는 의미입니다.

---

## 🔍 문제 진단 체크리스트

### 1. GCP VM에 SSH 키가 제대로 설정되어 있는가?

**GCP VM에 접속하여 확인**:

```bash
# 로컬에서 GCP VM에 접속
ssh user@YOUR_GCP_IP

# authorized_keys 파일 확인
cat ~/.ssh/authorized_keys

# 파일 권한 확인 (600이어야 함)
ls -la ~/.ssh/authorized_keys
```

**확인사항**:
- `~/.ssh/authorized_keys` 파일이 존재하는가?
- 파일 권한이 `600`인가?
- 파일 안에 공개 키가 있는가?

### 2. SSH 키 포맷이 올바른가?

GitHub Secrets에 저장할 **비밀 키**는 다음과 같은 형식이어야 합니다:

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
... (여러 줄) ...
AAAAAEC5AQAA
-----END OPENSSH PRIVATE KEY-----
```

**중요**:
- `-----BEGIN`과 `-----END` 라인 포함
- 줄바꿈 포함 (한 줄로 합치면 안 됨)
- 앞뒤 공백 없음

---

## 🔧 해결 방법

### 방법 1: SSH 키를 처음부터 다시 생성 (권장)

#### Step 1: GCP VM에서 새 SSH 키 생성

```bash
# GCP VM에 접속
ssh user@YOUR_GCP_IP

# 기존 키 백업 (있다면)
mv ~/.ssh/github_actions_key ~/.ssh/github_actions_key.bak 2>/dev/null

# 새 SSH 키 생성 (비밀번호 없이)
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_key -N ""

# 성공 메시지:
# Your identification has been saved in /home/user/.ssh/github_actions_key
# Your public key has been saved in /home/user/.ssh/github_actions_key.pub
```

#### Step 2: 공개 키를 authorized_keys에 추가

```bash
# 공개 키를 authorized_keys에 추가
cat ~/.ssh/github_actions_key.pub >> ~/.ssh/authorized_keys

# 중복 제거 (선택사항)
sort -u ~/.ssh/authorized_keys -o ~/.ssh/authorized_keys

# 권한 설정
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/github_actions_key
chmod 644 ~/.ssh/github_actions_key.pub

# 파일 확인
ls -la ~/.ssh/
```

#### Step 3: 비밀 키 복사

```bash
# 비밀 키 전체 내용 출력
cat ~/.ssh/github_actions_key
```

**출력 예시**:
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACBqM3c8pqKL5YhZ6BvVKXJKHpQ9LNJ7wZHGTKYzC5KNIAAAAJB1zK0Adcy
... (중략) ...
-----END OPENSSH PRIVATE KEY-----
```

**이 전체 내용을 복사하세요** (BEGIN부터 END까지 모두!)

#### Step 4: GitHub Secrets 업데이트

1. GitHub 저장소: https://github.com/ginger1541/xperion-wiki
2. **Settings** > **Secrets and variables** > **Actions**
3. `GCP_SSH_PRIVATE_KEY` 시크릿 찾기
4. **Update** 버튼 클릭
5. 위에서 복사한 **전체 내용** 붙여넣기 (BEGIN부터 END까지)
6. **Update secret** 클릭

#### Step 5: 다른 Secrets도 확인

**`GCP_HOST`** (IP 주소만):
```
34.29.153.88
```
(예시, 실제 GCP VM IP로 변경)

**`GCP_USERNAME`**:
```
user
```
(실제 사용자명으로 변경)

---

## 🧪 로컬에서 SSH 연결 테스트

GitHub Secrets를 업데이트한 후, **로컬에서** SSH 연결을 테스트하세요:

```bash
# GCP VM에서 비밀 키를 로컬로 복사 (안전한 방법)
# 방법 1: SCP 사용
scp user@YOUR_GCP_IP:~/.ssh/github_actions_key /tmp/test_key

# 권한 설정
chmod 600 /tmp/test_key

# SSH 연결 테스트
ssh -i /tmp/test_key user@YOUR_GCP_IP

# 성공하면 VM에 접속됨!
# 실패하면 아래 "추가 디버깅" 참고

# 테스트 완료 후 로컬 키 삭제
rm /tmp/test_key
```

**성공 조건**:
- 비밀번호 없이 바로 접속됨
- "Permission denied" 오류 없음

---

## 🔬 추가 디버깅

### SSH 상세 로그 확인

```bash
# verbose 모드로 SSH 연결 시도
ssh -vvv -i /tmp/test_key user@YOUR_GCP_IP

# 출력에서 확인할 내용:
# - "Offering public key" 메시지
# - "Server accepts key" 메시지
# - "Authentication succeeded" 메시지
```

### GCP VM의 SSH 데몬 로그 확인

```bash
# GCP VM에 접속 (다른 방법으로)
ssh user@YOUR_GCP_IP

# SSH 데몬 로그 확인
sudo journalctl -u ssh -n 50 --no-pager

# 또는
sudo tail -f /var/log/auth.log
```

**찾아볼 내용**:
- "Authentication refused" 메시지
- "bad ownership or modes" 경고

---

## 🎯 가장 흔한 원인

### 1. 비밀 키를 한 줄로 복사함
❌ 잘못된 예:
```
-----BEGIN OPENSSH PRIVATE KEY-----b3BlbnNzaC1rZXkt...AAAA-----END OPENSSH PRIVATE KEY-----
```

✅ 올바른 예:
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
...
-----END OPENSSH PRIVATE KEY-----
```

### 2. authorized_keys 파일 권한 문제
```bash
# 올바른 권한 설정
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### 3. SSH 키 타입 불일치
- GitHub Secrets의 비밀 키와 VM의 공개 키가 쌍이 맞아야 함
- 다른 키를 복사하지 않았는지 확인

### 4. 사용자명 또는 IP 주소 오류
- `GCP_HOST`: IP 주소만 (http:// 없이)
- `GCP_USERNAME`: 실제 VM 사용자명

---

## ✅ 최종 확인

모든 설정 후 다음을 확인:

1. **로컬에서 SSH 연결 성공**
   ```bash
   ssh -i /tmp/test_key user@YOUR_GCP_IP
   ```

2. **GitHub Secrets 3개 모두 설정됨**
   - GCP_HOST
   - GCP_USERNAME
   - GCP_SSH_PRIVATE_KEY

3. **워크플로우 재실행**
   - GitHub Actions 탭에서 "Re-run jobs" 클릭

---

## 📞 여전히 안 되나요?

다음 정보를 확인해주세요:

```bash
# GCP VM에서
whoami              # 사용자명 확인
hostname -I         # IP 주소 확인
ls -la ~/.ssh/      # SSH 디렉토리 확인
cat ~/.ssh/authorized_keys | wc -l  # 공개 키 개수
```

문제가 지속되면 위 정보와 함께 문의하세요.
