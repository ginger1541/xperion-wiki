#!/bin/bash
################################################################################
# Xperion Wiki 애플리케이션 업데이트 스크립트
#
# 코드 변경 후 배포할 때 사용
# 실행 방법: bash update-app.sh
################################################################################

set -e

echo "=================================="
echo "Xperion Wiki 애플리케이션 업데이트"
echo "=================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

APP_DIR="/home/$(whoami)/xperion-wiki"
VENV_DIR="${APP_DIR}/venv"

cd ${APP_DIR}

echo -e "${GREEN}1. Git 저장소 업데이트${NC}"
git fetch origin
git pull origin main

echo -e "${GREEN}2. Python 패키지 업데이트 (변경사항 있을 경우)${NC}"
cd ${APP_DIR}/backend
source ${VENV_DIR}/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}3. 데이터베이스 마이그레이션 확인${NC}"
alembic upgrade head

echo -e "${GREEN}4. 애플리케이션 재시작${NC}"
sudo systemctl restart xperion-wiki

# 재시작 후 상태 확인
sleep 3

if sudo systemctl is-active --quiet xperion-wiki; then
    echo -e "${GREEN}✅ 업데이트 완료!${NC}"
    echo ""
    sudo systemctl status xperion-wiki --no-pager -l
else
    echo -e "${RED}❌ 서비스 재시작 실패${NC}"
    echo "로그를 확인하세요:"
    sudo journalctl -u xperion-wiki -n 50 --no-pager
    exit 1
fi

echo ""
echo -e "${YELLOW}업데이트 후 확인사항:${NC}"
echo "1. API 응답 확인: curl http://localhost:8000/health"
echo "2. 로그 모니터링: sudo journalctl -u xperion-wiki -f"
