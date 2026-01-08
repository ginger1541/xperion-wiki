#!/bin/bash
################################################################################
# PostgreSQL 데이터베이스 백업 스크립트
#
# 실행 방법: bash backup-database.sh
# Cron 설정 (매일 새벽 3시): 0 3 * * * /home/user/xperion-wiki/backend/scripts/deploy/gcp/backup-database.sh
################################################################################

set -e

# 설정
DB_NAME="xperion_wiki"
DB_USER="xperion"
BACKUP_DIR="/home/$(whoami)/backups/database"
RETENTION_DAYS=7  # 7일간 백업 보관

# 백업 디렉토리 생성
mkdir -p ${BACKUP_DIR}

# 백업 파일명 (날짜_시간 형식)
BACKUP_FILE="${BACKUP_DIR}/xperion_wiki_$(date +%Y%m%d_%H%M%S).sql.gz"

echo "=================================="
echo "Database Backup Started"
echo "=================================="
echo "Timestamp: $(date)"
echo "Backup file: ${BACKUP_FILE}"

# PostgreSQL 백업 (압축)
pg_dump -U ${DB_USER} -h localhost ${DB_NAME} | gzip > ${BACKUP_FILE}

if [ $? -eq 0 ]; then
    echo "✅ Backup completed successfully"
    echo "File size: $(du -h ${BACKUP_FILE} | cut -f1)"

    # 오래된 백업 삭제 (retention policy)
    find ${BACKUP_DIR} -name "*.sql.gz" -mtime +${RETENTION_DAYS} -delete
    echo "Cleaned up backups older than ${RETENTION_DAYS} days"
else
    echo "❌ Backup failed"
    exit 1
fi

# GitHub에도 백업 (선택사항 - Source of Truth이므로)
echo "Note: Main data is in GitHub repository (Source of Truth)"
echo "This backup is for PostgreSQL metadata only"
