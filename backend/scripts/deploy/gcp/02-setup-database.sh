#!/bin/bash
################################################################################
# PostgreSQL 데이터베이스 설정 스크립트
#
# 실행 방법: bash 02-setup-database.sh
################################################################################

set -e

echo "=================================="
echo "PostgreSQL 데이터베이스 설정"
echo "=================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 데이터베이스 설정
DB_NAME="xperion_wiki"
DB_USER="xperion"

echo -e "${YELLOW}데이터베이스 비밀번호를 입력하세요:${NC}"
read -s DB_PASSWORD
echo ""

echo -e "${GREEN}1. PostgreSQL 데이터베이스 생성${NC}"
sudo -u postgres psql <<EOF
-- 데이터베이스 생성
CREATE DATABASE ${DB_NAME};

-- 사용자 생성
CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';

-- 권한 부여
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};

-- PostgreSQL 15+ 추가 권한
\c ${DB_NAME}
GRANT ALL ON SCHEMA public TO ${DB_USER};
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${DB_USER};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${DB_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${DB_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${DB_USER};

-- pg_trgm extension 활성화 (검색용)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

\q
EOF

echo -e "${GREEN}2. PostgreSQL 연결 테스트${NC}"
PGPASSWORD=${DB_PASSWORD} psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "SELECT version();"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 데이터베이스 설정 완료!${NC}"
    echo ""
    echo -e "${YELLOW}환경 변수 설정 정보:${NC}"
    echo "DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}"
    echo ""
    echo -e "${YELLOW}이 값을 .env 파일에 저장하세요!${NC}"
else
    echo -e "${RED}❌ 데이터베이스 연결 실패${NC}"
    exit 1
fi
