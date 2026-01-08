# SSH 키 설정 검증 가이드

이 가이드는 GitHub Actions CI/CD를 위한 SSH 키가 올바르게 설정되었는지 확인합니다.

---

## ✅ 체크리스트

### 1️⃣ GCP VM에서 실행 (SSH로 접속 후)

```bash
# GCP VM에 접속
ssh user@YOUR_GCP_IP

# 다음 명령어들을 순서대로 실행하세요
```

#### Step 1: SSH 디렉토리 및 파일 확인

```bash
echo "=== SSH 디렉토리 확인 ==="
ls -la ~/.ssh/

echo -e "\n=== authorized_keys 파일 존재 확인 ==="
[ -f ~/.ssh/authorized_keys ] && echo "✅ authorized_keys 파일 존재" || echo "❌ authorized_keys 파일 없음"

echo -e "\n=== github_actions_key 파일 존재 확인 ==="
[ -f ~/.ssh/github_actions_key ] && echo "✅ github_actions_key 파일 존재" || echo "❌ github_actions_key 파일 없음"
[ -f ~/.ssh/github_actions_key.pub ] && echo "✅ github_actions_key.pub 파일 존재" || echo "❌ github_actions_key.pub 파일 없음"
```

**예상 출력**:
```
drwx------  2 user user 4096 Jan  8 07:00 .ssh
-rw-------  1 user user  411 Jan  8 07:00 authorized_keys
-rw-------  1 user user  411 Jan  8 07:00 github_actions_key
-rw-r--r--  1 user user   99 Jan  8 07:00 github_actions_key.pub
```

**권한 확인**:
- `.ssh/` 디렉토리: `700` (drwx------)
- `authorized_keys`: `600` (-rw-------)
- `github_actions_key`: `600` (-rw-------)

#### Step 2: 권한 수정 (필요시)

```bash
echo "=== 권한 수정 ==="
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/github_actions_key
chmod 644 ~/.ssh/github_actions_key.pub

echo "✅ 권한 수정 완료"
```

#### Step 3: 공개 키가 authorized_keys에 있는지 확인

```bash
echo "=== 공개 키 확인 ==="
echo "github_actions_key.pub 내용:"
cat ~/.ssh/github_actions_key.pub

echo -e "\nauthorized_keys에서 해당 키 찾기:"
grep -f ~/.ssh/github_actions_key.pub ~/.ssh/authorized_keys && echo "✅ 공개 키가 authorized_keys에 존재" || echo "❌ 공개 키가 authorized_keys에 없음"
```

**만약 "공개 키가 없음"이 표시되면**:
```bash
# 공개 키를 authorized_keys에 추가
cat ~/.ssh/github_actions_key.pub >> ~/.ssh/authorized_keys
echo "✅ 공개 키 추가 완료"
```

#### Step 4: 비밀 키 형식 확인

```bash
echo "=== 비밀 키 형식 확인 ==="
head -n 1 ~/.ssh/github_actions_key
tail -n 1 ~/.ssh/github_actions_key

echo -e "\n=== 비밀 키 전체 줄 수 ==="
wc -l ~/.ssh/github_actions_key
```

**예상 출력**:
```
-----BEGIN OPENSSH PRIVATE KEY-----
-----END OPENSSH PRIVATE KEY-----

6 /home/user/.ssh/github_actions_key
```

#### Step 5: 비밀 키 전체 출력 (GitHub Secrets용)

```bash
echo "=== 비밀 키 전체 내용 (복사하세요) ==="
cat ~/.ssh/github_actions_key
echo "=== 끝 ==="
```

**⚠️ 중요**: 이 출력 전체를 복사하여 GitHub Secrets의 `GCP_SSH_PRIVATE_KEY`에 붙여넣으세요.
- `-----BEGIN OPENSSH PRIVATE KEY-----`부터 시작
- `-----END OPENSSH PRIVATE KEY-----`로 끝남
- **모든 줄바꿈 포함**

#### Step 6: 로컬에서 SSH 연결 테스트

```bash
# GCP VM에서 로컬로 키 복사
scp ~/.ssh/github_actions_key YOUR_LOCAL_USER@YOUR_LOCAL_IP:/tmp/test_key

# 또는 내용을 복사하여 로컬에 파일 생성
cat ~/.ssh/github_actions_key
# (위 내용을 복사하여 로컬의 /tmp/test_key에 붙여넣기)
```

**로컬 컴퓨터에서**:
```bash
# 권한 설정
chmod 600 /tmp/test_key

# SSH 연결 테스트
ssh -i /tmp/test_key user@YOUR_GCP_IP

# 성공하면 비밀번호 없이 바로 접속됨!
```

**연결 성공 시**:
```
Welcome to Ubuntu...
user@instance-name:~$
```

**연결 실패 시** (verbose 모드로 재시도):
```bash
ssh -vvv -i /tmp/test_key user@YOUR_GCP_IP
```

로그에서 다음을 찾아보세요:
- "Offering public key" - 키를 제공하는 중
- "Server accepts key" - 서버가 키를 수락함
- "Authentication succeeded" - 인증 성공
- "Permission denied" - 인증 실패

---

### 2️⃣ GitHub Secrets 확인

#### GitHub Secrets 페이지로 이동
https://github.com/ginger1541/xperion-wiki/settings/secrets/actions

#### 확인할 3개의 Secrets

**1. GCP_HOST**
- ✅ 값 형식: `34.29.153.88` (IP 주소만, http:// 없이)
- ❌ 잘못된 예: `http://34.29.153.88`, `user@34.29.153.88`

**2. GCP_USERNAME**
- ✅ 값 형식: `user` (사용자명만)
- ❌ 잘못된 예: `user@host`, `/home/user`

**3. GCP_SSH_PRIVATE_KEY**
- ✅ 올바른 형식:
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmU...
(여러 줄)
...AAAAAEC5AQAA
-----END OPENSSH PRIVATE KEY-----
```

**복사할 때 주의사항**:
1. 전체 내용 복사 (BEGIN부터 END까지)
2. 줄바꿈 유지 (한 줄로 만들지 마세요)
3. 앞뒤 공백 제거
4. 다른 텍스트 포함하지 않기

---

### 3️⃣ 대안: RSA 키 사용 (ED25519가 안 될 경우)

ED25519 키로 안 되면 RSA 키를 시도해보세요:

```bash
# GCP VM에서
ssh-keygen -t rsa -b 4096 -C "github-actions-deploy" -f ~/.ssh/github_actions_key_rsa -N ""

# 공개 키를 authorized_keys에 추가
cat ~/.ssh/github_actions_key_rsa.pub >> ~/.ssh/authorized_keys

# 권한 설정
chmod 600 ~/.ssh/github_actions_key_rsa

# 비밀 키 출력 (GitHub Secrets에 붙여넣기)
cat ~/.ssh/github_actions_key_rsa
```

---

### 4️⃣ SSHD 설정 확인 (필요시)

만약 계속 실패한다면 GCP VM의 SSH 데몬 설정을 확인하세요:

```bash
# GCP VM에서
sudo cat /etc/ssh/sshd_config | grep -E "PubkeyAuthentication|AuthorizedKeysFile"
```

**예상 출력**:
```
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
```

만약 `PubkeyAuthentication no`로 되어 있다면:
```bash
sudo nano /etc/ssh/sshd_config
# PubkeyAuthentication을 yes로 변경

# SSH 데몬 재시작
sudo systemctl restart sshd
```

---

## 🎯 최종 점검 체크리스트

실행 전 다음을 모두 확인하세요:

- [ ] GCP VM의 `~/.ssh/authorized_keys`에 공개 키가 있음
- [ ] `~/.ssh/authorized_keys` 권한이 600임
- [ ] 로컬에서 SSH 키로 연결 테스트 성공
- [ ] GitHub Secrets의 `GCP_HOST`가 IP 주소만 포함
- [ ] GitHub Secrets의 `GCP_USERNAME`이 정확함
- [ ] GitHub Secrets의 `GCP_SSH_PRIVATE_KEY`가 전체 키 내용 (줄바꿈 포함)
- [ ] 비밀 키가 `-----BEGIN`과 `-----END` 포함

모두 체크되면 GitHub Actions 워크플로우를 다시 실행하세요!

---

## 📞 추가 도움

위 단계를 모두 따랐는데도 실패한다면 다음 정보를 공유해주세요:

```bash
# GCP VM에서 실행
echo "=== 시스템 정보 ==="
whoami
hostname -I
ls -la ~/.ssh/
wc -l ~/.ssh/github_actions_key
head -n 1 ~/.ssh/github_actions_key
tail -n 1 ~/.ssh/github_actions_key
```
