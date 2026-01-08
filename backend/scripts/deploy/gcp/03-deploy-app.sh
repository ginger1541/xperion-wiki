#!/bin/bash
################################################################################
# Xperion Wiki 애플리케이션 배포 스크립트
#
# 실행 방법: bash 03-deploy-app.sh
################################################################################

set -e

echo "=================================="
echo "Xperion Wiki 애플리케이션 배포"
echo "=================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 설정
APP_DIR="/home/$(whoami)/xperion-wiki"
VENV_DIR="${APP_DIR}/venv"

echo -e "${YELLOW}GitHub Repository URL을 입력하세요:${NC}"
echo "(예: https://github.com/username/xperion-wiki.git)"
read REPO_URL

echo -e "${GREEN}1. 프로젝트 클론${NC}"
if [ -d "${APP_DIR}" ]; then
    echo "프로젝트 디렉토리가 이미 존재합니다. 업데이트합니다."
    cd ${APP_DIR}
    git pull
else
    git clone ${REPO_URL} ${APP_DIR}
    cd ${APP_DIR}
fi

echo -e "${GREEN}2. Python 가상환경 생성${NC}"
cd ${APP_DIR}/backend
if [ ! -d "${VENV_DIR}" ]; then
    python3.11 -m venv ${VENV_DIR}
fi

echo -e "${GREEN}3. Python 패키지 설치${NC}"
source ${VENV_DIR}/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}4. 환경 변수 설정${NC}"
if [ ! -f "${APP_DIR}/backend/.env" ]; then
    echo -e "${YELLOW}.env 파일을 생성합니다.${NC}"
    echo ""

    echo "DATABASE_URL을 입력하세요:"
    echo "(예: postgresql+asyncpg://xperion:password@localhost:5432/xperion_wiki)"
    read DATABASE_URL

    echo "GITHUB_TOKEN을 입력하세요:"
    read -s GITHUB_TOKEN
    echo ""

    echo "GITHUB_REPO를 입력하세요:"
    echo "(예: username/xperion-wiki-content)"
    read GITHUB_REPO

    echo "SECRET_KEY를 입력하세요 (엔터 시 자동 생성):"
    read SECRET_KEY
    if [ -z "${SECRET_KEY}" ]; then
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    fi

    echo "CORS_ORIGINS를 입력하세요:"
    echo "(예: https://xperion-wiki.vercel.app,http://localhost:5173)"
    read CORS_ORIGINS

    cat > ${APP_DIR}/backend/.env <<EOF
# Database
DATABASE_URL=${DATABASE_URL}

# GitHub
GITHUB_TOKEN=${GITHUB_TOKEN}
GITHUB_REPO=${GITHUB_REPO}
GITHUB_BRANCH=main

# Security
SECRET_KEY=${SECRET_KEY}

# CORS
CORS_ORIGINS=${CORS_ORIGINS}

# App
APP_NAME=Xperion Wiki API
VERSION=0.1.0
ENVIRONMENT=production
EOF

    echo -e "${GREEN}.env 파일 생성 완료!${NC}"
else
    echo -e "${YELLOW}.env 파일이 이미 존재합니다.${NC}"
fi

echo -e "${GREEN}5. 데이터베이스 마이그레이션${NC}"
cd ${APP_DIR}/backend
source ${VENV_DIR}/bin/activate
alembic upgrade head

echo -e "${GREEN}6. systemd 서비스 생성${NC}"
sudo tee /etc/systemd/system/xperion-wiki.service > /dev/null <<EOF
[Unit]
Description=Xperion Wiki FastAPI Application
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=$(whoami)
Group=$(whoami)
WorkingDirectory=${APP_DIR}/backend
Environment="PATH=${VENV_DIR}/bin"
ExecStart=${VENV_DIR}/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
Restart=always
RestartSec=10

# 보안 설정
NoNewPrivileges=true
PrivateTmp=true

# 리소스 제한 (1GB RAM 환경)
MemoryMax=400M
MemoryHigh=300M

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}7. 서비스 활성화 및 시작${NC}"
sudo systemctl daemon-reload
sudo systemctl enable xperion-wiki
sudo systemctl start xperion-wiki

# 서비스 상태 확인
sleep 2
if sudo systemctl is-active --quiet xperion-wiki; then
    echo -e "${GREEN}✅ 애플리케이션 배포 완료!${NC}"
    echo ""
    sudo systemctl status xperion-wiki --no-pager -l
    echo ""
    echo -e "${YELLOW}다음 단계:${NC}"
    echo "bash 04-setup-nginx.sh  # Nginx 설정"
else
    echo -e "${RED}❌ 서비스 시작 실패${NC}"
    sudo journalctl -u xperion-wiki -n 50 --no-pager
    exit 1
fi
