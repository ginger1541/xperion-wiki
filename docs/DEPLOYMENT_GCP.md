# Xperion Wiki - GCP 배포 가이드

GCP Compute Engine e2-micro (무료 티어)를 사용한 완전 무료 배포 가이드입니다.

---

## 목차

1. [사전 준비](#사전-준비)
2. [GCP VM 생성](#gcp-vm-생성)
3. [서버 초기 설정](#서버-초기-설정)
4. [데이터베이스 설정](#데이터베이스-설정)
5. [애플리케이션 배포](#애플리케이션-배포)
6. [Nginx 및 SSL 설정](#nginx-및-ssl-설정)
7. [운영 및 유지보수](#운영-및-유지보수)
8. [트러블슈팅](#트러블슈팅)

---

## 사전 준비

### 필요한 것

1. **GCP 계정**
   - 신규 가입 시 $300 크레딧 (90일)
   - e2-micro는 Always Free 티어 (크레딧과 별개)

2. **GitHub Repository**
   - 코드 저장용 (Private)
   - 마크다운 문서 저장용 (Private)

3. **도메인 (선택사항)**
   - SSL 인증서 발급 시 필요
   - 없으면 IP 주소로 접근 가능

4. **로컬 환경**
   - gcloud CLI 설치 (또는 GCP Console 사용)

---

## GCP VM 생성

### 옵션 1: GCP Console (웹 UI)

1. **GCP Console 접속**
   - https://console.cloud.google.com

2. **프로젝트 생성**
   - 프로젝트 이름: `xperion-wiki`
   - 프로젝트 ID 기록 (나중에 필요)

3. **Compute Engine 활성화**
   - 메뉴 → Compute Engine → VM 인스턴스
   - API 활성화 (처음 한 번만)

4. **VM 인스턴스 생성**
   - 이름: `xperion-wiki-server`
   - 리전: `us-central1` (또는 `us-east1`, `us-west1`)
     - ⚠️ **중요: Always Free는 US 리전만 지원**
   - 머신 구성:
     - 시리즈: E2
     - 머신 유형: **e2-micro** (2 vCPU, 1GB RAM)
   - 부팅 디스크:
     - 운영체제: Ubuntu
     - 버전: Ubuntu 22.04 LTS
     - 크기: 30GB (기본값)
   - 방화벽:
     - ✅ HTTP 트래픽 허용
     - ✅ HTTPS 트래픽 허용

5. **만들기 클릭**

### 옵션 2: gcloud CLI

```bash
# gcloud CLI 설치 확인
gcloud --version

# GCP 로그인
gcloud auth login

# 프로젝트 설정
gcloud config set project YOUR_PROJECT_ID

# VM 생성
gcloud compute instances create xperion-wiki-server \
    --zone=us-central1-a \
    --machine-type=e2-micro \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=30GB \
    --boot-disk-type=pd-standard \
    --tags=http-server,https-server

# 방화벽 규칙 생성 (HTTP/HTTPS)
gcloud compute firewall-rules create allow-http \
    --allow tcp:80 \
    --target-tags http-server

gcloud compute firewall-rules create allow-https \
    --allow tcp:443 \
    --target-tags https-server
```

### VM 접속

```bash
# GCP Console에서
VM 인스턴스 목록 → SSH 버튼 클릭

# gcloud CLI에서
gcloud compute ssh xperion-wiki-server --zone=us-central1-a
```

---

## 서버 초기 설정

### 1. 설정 스크립트 다운로드

```bash
# VM에 SSH 접속 후
cd ~
git clone https://github.com/YOUR_USERNAME/xperion-wiki.git
cd xperion-wiki/backend/scripts/deploy/gcp
chmod +x *.sh
```

### 2. 초기 설정 실행

```bash
bash 01-setup-vm.sh
```

**이 스크립트가 하는 일:**
- 시스템 업데이트
- Python 3.11 설치
- PostgreSQL 15 설치
- Nginx 설치
- Certbot 설치 (SSL용)
- 방화벽 설정
- 2GB Swap 메모리 생성 (1GB RAM 보완)
- PostgreSQL 메모리 최적화

**예상 소요 시간:** 5-10분

---

## 데이터베이스 설정

### 1. PostgreSQL 설정 실행

```bash
bash 02-setup-database.sh
```

**입력 정보:**
- 데이터베이스 비밀번호 (안전한 비밀번호 생성)
- 예: `openssl rand -base64 32`

### 2. 출력된 DATABASE_URL 저장

스크립트 완료 후 다음과 같은 형식으로 출력됩니다:

```
DATABASE_URL=postgresql+asyncpg://xperion:YOUR_PASSWORD@localhost:5432/xperion_wiki
```

**이 값을 복사해두세요!** (다음 단계에서 필요)

---

## 애플리케이션 배포

### 1. GitHub Repository 준비

#### 코드 저장소 (이미 있음)
```
https://github.com/YOUR_USERNAME/xperion-wiki.git
```

#### 문서 저장소 생성 (새로 만들기)

GCP에서:
1. GitHub에서 새 Private Repository 생성
2. 이름: `xperion-wiki-content`
3. README.md 추가
4. `docs/` 폴더 생성

### 2. GitHub Personal Access Token 발급

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Note: `Xperion Wiki Server`
4. Scopes:
   - ✅ `repo` (전체)
5. Generate token
6. **토큰 복사** (한 번만 표시됨!)

### 3. 애플리케이션 배포 실행

```bash
bash 03-deploy-app.sh
```

**입력 정보:**

1. **GitHub Repository URL**
   ```
   https://github.com/YOUR_USERNAME/xperion-wiki.git
   ```

2. **DATABASE_URL**
   - 이전 단계에서 복사한 값 입력

3. **GITHUB_TOKEN**
   - Personal Access Token 입력

4. **GITHUB_REPO**
   ```
   YOUR_USERNAME/xperion-wiki-content
   ```

5. **SECRET_KEY**
   - 엔터 (자동 생성)

6. **CORS_ORIGINS**
   ```
   https://your-frontend.vercel.app,http://localhost:5173
   ```
   - Vercel 배포 후 실제 URL로 변경

**예상 소요 시간:** 3-5분

### 4. 배포 확인

```bash
# 서비스 상태 확인
sudo systemctl status xperion-wiki

# API 테스트
curl http://localhost:8000/health
# 출력: {"status":"healthy"}

# 로그 확인
sudo journalctl -u xperion-wiki -n 50
```

---

## Nginx 및 SSL 설정

### 1. 도메인 DNS 설정 (도메인 사용 시)

GCP VM의 외부 IP 확인:
```bash
curl ifconfig.me
```

도메인 DNS에 A 레코드 추가:
```
api.xperion-wiki.com  →  YOUR_VM_IP
```

### 2. Nginx 설정 실행

```bash
bash 04-setup-nginx.sh
```

**입력 정보:**

1. **도메인 이름**
   - 도메인 있음: `api.xperion-wiki.com`
   - 도메인 없음: VM의 외부 IP 주소

2. **이메일 주소**
   - SSL 인증서 발급용

3. **SSL 발급 여부**
   - 도메인 사용 시: `y`
   - IP 주소 사용 시: SSL 불가

### 3. 배포 완료 확인

#### 도메인 사용 시
```bash
curl https://api.xperion-wiki.com/health
```

#### IP 주소 사용 시
```bash
curl http://YOUR_VM_IP/health
```

#### Swagger UI 접속
- 도메인: `https://api.xperion-wiki.com/docs`
- IP: `http://YOUR_VM_IP/docs`

---

## 프론트엔드 연결 (Vercel)

### 1. 환경 변수 설정

Vercel 프로젝트 → Settings → Environment Variables:

```
VITE_API_URL=https://api.xperion-wiki.com
# 또는
VITE_API_URL=http://YOUR_VM_IP
```

### 2. 재배포

Vercel에서 자동으로 재배포되거나, 수동으로 Redeploy 실행

### 3. CORS 업데이트

Vercel 배포 완료 후 실제 URL 확인하여:

```bash
# VM에서
cd /home/YOUR_USERNAME/xperion-wiki/backend
nano .env

# CORS_ORIGINS 수정
CORS_ORIGINS=https://xperion-wiki.vercel.app,http://localhost:5173

# 서비스 재시작
sudo systemctl restart xperion-wiki
```

---

## 운영 및 유지보수

### 일상적인 명령어

```bash
# 서비스 상태 확인
sudo systemctl status xperion-wiki

# 서비스 재시작
sudo systemctl restart xperion-wiki

# 실시간 로그 보기
sudo journalctl -u xperion-wiki -f

# Nginx 로그
sudo tail -f /var/log/nginx/xperion-wiki-error.log
sudo tail -f /var/log/nginx/xperion-wiki-access.log

# 서버 리소스 확인
htop
free -h  # 메모리 사용량
df -h    # 디스크 사용량
```

### 코드 업데이트

```bash
cd ~/xperion-wiki/backend/scripts/deploy/gcp
bash update-app.sh
```

### 데이터베이스 백업

#### 수동 백업
```bash
cd ~/xperion-wiki/backend/scripts/deploy/gcp
bash backup-database.sh
```

#### 자동 백업 설정 (Cron)
```bash
# crontab 편집
crontab -e

# 매일 새벽 3시 백업 추가
0 3 * * * /home/YOUR_USERNAME/xperion-wiki/backend/scripts/deploy/gcp/backup-database.sh
```

### SSL 인증서 자동 갱신

Let's Encrypt 인증서는 90일마다 갱신 필요:

```bash
# 자동 갱신 테스트
sudo certbot renew --dry-run

# Certbot이 자동으로 cron 설정함 (확인)
sudo systemctl list-timers | grep certbot
```

---

## 트러블슈팅

### 1. 서비스가 시작되지 않음

```bash
# 로그 확인
sudo journalctl -u xperion-wiki -n 100

# 일반적인 문제:
# - .env 파일 누락 → 03-deploy-app.sh 재실행
# - DATABASE_URL 오류 → .env 파일 수정
# - 포트 충돌 → sudo lsof -i :8000
```

### 2. 메모리 부족 (OOM)

```bash
# 메모리 사용량 확인
free -h

# Swap 확인
swapon --show

# PostgreSQL 메모리 설정 축소
sudo nano /etc/postgresql/15/main/postgresql.conf
# shared_buffers = 64MB (128MB → 64MB)

sudo systemctl restart postgresql
```

### 3. 503 Bad Gateway (Nginx)

```bash
# FastAPI 서비스 확인
sudo systemctl status xperion-wiki

# 포트 확인
sudo lsof -i :8000

# Nginx 재시작
sudo systemctl restart nginx
```

### 4. SSL 인증서 발급 실패

```bash
# DNS 전파 확인
nslookup api.xperion-wiki.com

# 포트 80 접근 확인
curl http://api.xperion-wiki.com

# Certbot 로그 확인
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

### 5. GitHub 연동 오류

```bash
# GitHub Token 권한 확인
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user

# .env 파일 확인
cat ~/xperion-wiki/backend/.env | grep GITHUB

# 서비스 재시작
sudo systemctl restart xperion-wiki
```

### 6. 데이터베이스 연결 오류

```bash
# PostgreSQL 상태 확인
sudo systemctl status postgresql

# 연결 테스트
psql -h localhost -U xperion -d xperion_wiki

# pg_trgm extension 확인
psql -h localhost -U xperion -d xperion_wiki -c "\dx"
```

---

## 비용 관리

### Always Free 티어 한도

- ✅ e2-micro: 1대, 720시간/월 (24/7 가능)
- ✅ 디스크: 30GB 표준 영구 디스크
- ✅ 트래픽: 1GB 아웃바운드/월

### 초과 시 과금

```
트래픽 초과: $0.12/GB
→ 10GB 초과해도 $1.2
```

### 비용 모니터링

```bash
# GCP Console → Billing → 비용 보고서
# 알림 설정: 예산 $5 초과 시 이메일 알림
```

---

## 성능 최적화

### 1GB RAM 환경에서의 팁

1. **Worker 수 최소화**
   - FastAPI workers: 1개 (systemd 설정)

2. **PostgreSQL 튜닝**
   - shared_buffers: 128MB
   - max_connections: 20

3. **Swap 활용**
   - 2GB Swap 설정됨
   - swappiness: 10 (메모리 우선)

4. **불필요한 서비스 비활성화**
   ```bash
   sudo systemctl disable snapd
   sudo systemctl stop snapd
   ```

---

## 보안 체크리스트

- ✅ SSH 키 인증만 허용 (비밀번호 비활성화)
- ✅ 방화벽 설정 (ufw)
- ✅ PostgreSQL 외부 접근 차단 (localhost만)
- ✅ .env 파일 권한 (`chmod 600`)
- ✅ SSL 인증서 사용
- ✅ 정기 백업 설정
- ✅ OS 보안 업데이트

```bash
# 보안 업데이트 자동 설치
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 다음 단계

1. ✅ 서버 배포 완료
2. ✅ 프론트엔드 연결
3. 📝 초기 데이터 입력 (시드 데이터)
4. 🧪 통합 테스트
5. 👥 멤버 초대 및 사용법 안내
6. 📊 모니터링 설정 (선택사항)

---

## 참고 자료

- [GCP Always Free Tier](https://cloud.google.com/free/docs/free-cloud-features)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL 성능 튜닝](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Nginx 리버스 프록시](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [Let's Encrypt](https://letsencrypt.org/getting-started/)

---

## 문의

문제가 발생하면:
1. 이 문서의 트러블슈팅 섹션 확인
2. GitHub Issues에 버그 리포트
3. 로그 파일 첨부 (`journalctl`, nginx logs)
