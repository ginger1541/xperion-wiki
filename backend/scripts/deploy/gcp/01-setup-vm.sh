#!/bin/bash
################################################################################
# GCP e2-micro VM 초기 설정 스크립트
#
# 이 스크립트는 새로 생성된 Ubuntu VM에서 실행됩니다.
# 실행 방법: bash 01-setup-vm.sh
################################################################################

set -e  # 에러 발생 시 즉시 중단

echo "=================================="
echo "Xperion Wiki - GCP VM 초기 설정"
echo "=================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 현재 사용자
CURRENT_USER=$(whoami)

echo -e "${GREEN}1. 시스템 업데이트${NC}"
sudo apt update
sudo apt upgrade -y

echo -e "${GREEN}2. 기본 패키지 설치${NC}"
sudo apt install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    build-essential \
    software-properties-common

echo -e "${GREEN}3. Python 3.11 설치${NC}"
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip

# Python 3.11을 기본으로 설정
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

echo -e "${GREEN}4. PostgreSQL 15 설치${NC}"
sudo apt install -y postgresql-15 postgresql-contrib-15 postgresql-client-15

# PostgreSQL 서비스 시작
sudo systemctl enable postgresql
sudo systemctl start postgresql

echo -e "${GREEN}5. Nginx 설치${NC}"
sudo apt install -y nginx

echo -e "${GREEN}6. Certbot (Let's Encrypt SSL) 설치${NC}"
sudo apt install -y certbot python3-certbot-nginx

echo -e "${GREEN}7. 방화벽 설정${NC}"
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw --force enable

echo -e "${GREEN}8. Swap 메모리 설정 (2GB)${NC}"
# e2-micro는 1GB RAM이므로 Swap 필수
if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile

    # 재부팅 후에도 유지
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

    # Swap 사용 최적화
    sudo sysctl vm.swappiness=10
    echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
fi

echo -e "${GREEN}9. PostgreSQL 메모리 최적화 (1GB RAM 환경)${NC}"
sudo tee -a /etc/postgresql/15/main/postgresql.conf > /dev/null <<EOF

# Xperion Wiki - 1GB RAM 최적화
shared_buffers = 128MB
effective_cache_size = 256MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 6MB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 2
max_parallel_workers_per_gather = 1
max_parallel_workers = 2
max_parallel_maintenance_workers = 1
max_connections = 20
EOF

sudo systemctl restart postgresql

echo -e "${GREEN}10. Git 전역 설정${NC}"
git config --global user.name "Xperion Wiki Server"
git config --global user.email "server@xperion-wiki.local"

echo ""
echo -e "${GREEN}=================================="
echo -e "✅ VM 초기 설정 완료!"
echo -e "==================================${NC}"
echo ""
echo -e "${YELLOW}다음 단계:${NC}"
echo "1. bash 02-setup-database.sh  # 데이터베이스 설정"
echo "2. bash 03-deploy-app.sh      # 애플리케이션 배포"
echo ""
