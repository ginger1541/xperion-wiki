# GCP 배포 스크립트

GCP Compute Engine e2-micro (무료 티어) 배포를 위한 자동화 스크립트입니다.

## 사용 방법

### 초기 배포 (순서대로 실행)

```bash
# 1. VM 초기 설정
bash 01-setup-vm.sh

# 2. 데이터베이스 설정
bash 02-setup-database.sh

# 3. 애플리케이션 배포
bash 03-deploy-app.sh

# 4. Nginx 및 SSL 설정
bash 04-setup-nginx.sh
```

### 운영 스크립트

```bash
# 코드 업데이트
bash update-app.sh

# 데이터베이스 백업
bash backup-database.sh
```

## 스크립트 설명

### 01-setup-vm.sh
- 시스템 업데이트
- Python 3.11, PostgreSQL 15, Nginx 설치
- Swap 메모리 설정 (2GB)
- 방화벽 설정
- PostgreSQL 메모리 최적화

### 02-setup-database.sh
- PostgreSQL 데이터베이스 생성
- 사용자 및 권한 설정
- pg_trgm extension 활성화
- DATABASE_URL 생성

### 03-deploy-app.sh
- Git 저장소 클론
- Python 가상환경 생성
- 패키지 설치
- .env 파일 생성
- 데이터베이스 마이그레이션
- systemd 서비스 등록 및 시작

### 04-setup-nginx.sh
- Nginx 리버스 프록시 설정
- SSL 인증서 발급 (Let's Encrypt)
- HTTPS 리다이렉트

### update-app.sh
- Git pull
- 패키지 업데이트
- 데이터베이스 마이그레이션
- 서비스 재시작

### backup-database.sh
- PostgreSQL 덤프 생성
- 압축 (gzip)
- 7일 이상 백업 삭제

## 요구사항

- GCP Compute Engine e2-micro VM
- Ubuntu 22.04 LTS
- 인터넷 연결

## 상세 가이드

전체 배포 가이드는 `/docs/DEPLOYMENT_GCP.md`를 참조하세요.

## 트러블슈팅

### 스크립트 실행 권한 오류
```bash
chmod +x *.sh
```

### 서비스 상태 확인
```bash
sudo systemctl status xperion-wiki
sudo journalctl -u xperion-wiki -f
```

### Nginx 로그 확인
```bash
sudo tail -f /var/log/nginx/xperion-wiki-error.log
```
