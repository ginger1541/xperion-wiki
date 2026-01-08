#!/bin/bash
################################################################################
# Nginx 설정 및 SSL 인증서 발급 스크립트
#
# 실행 방법: bash 04-setup-nginx.sh
################################################################################

set -e

echo "=================================="
echo "Nginx 및 SSL 설정"
echo "=================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}도메인 이름을 입력하세요:${NC}"
echo "(예: api.xperion-wiki.com 또는 GCP 외부 IP 주소)"
read DOMAIN

echo -e "${YELLOW}이메일 주소를 입력하세요 (SSL 인증서용):${NC}"
read EMAIL

echo -e "${GREEN}1. 기본 Nginx 설정 삭제${NC}"
sudo rm -f /etc/nginx/sites-enabled/default

echo -e "${GREEN}2. Xperion Wiki Nginx 설정 생성${NC}"
sudo tee /etc/nginx/sites-available/xperion-wiki > /dev/null <<EOF
server {
    listen 80;
    server_name ${DOMAIN};

    # 로그 설정
    access_log /var/log/nginx/xperion-wiki-access.log;
    error_log /var/log/nginx/xperion-wiki-error.log;

    # 최대 업로드 크기 (이미지 업로드용)
    client_max_body_size 10M;

    # FastAPI 프록시
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # WebSocket 지원 (향후 실시간 기능용)
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";

        # 타임아웃 설정
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check (캐싱 없음)
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host \$host;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
}
EOF

echo -e "${GREEN}3. Nginx 설정 심볼릭 링크 생성${NC}"
sudo ln -sf /etc/nginx/sites-available/xperion-wiki /etc/nginx/sites-enabled/

echo -e "${GREEN}4. Nginx 설정 테스트${NC}"
sudo nginx -t

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Nginx 설정 오류${NC}"
    exit 1
fi

echo -e "${GREEN}5. Nginx 재시작${NC}"
sudo systemctl restart nginx

# 도메인이 IP 주소인지 확인
if [[ $DOMAIN =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${YELLOW}경고: IP 주소로는 SSL 인증서를 발급할 수 없습니다.${NC}"
    echo -e "${YELLOW}도메인 이름을 사용하려면 DNS를 설정한 후 다시 실행하세요.${NC}"
    echo ""
    echo -e "${GREEN}✅ Nginx 설정 완료!${NC}"
    echo "API 접속: http://${DOMAIN}"
else
    echo -e "${GREEN}6. SSL 인증서 발급 (Let's Encrypt)${NC}"
    echo -e "${YELLOW}SSL 인증서를 발급하시겠습니까? (y/n)${NC}"
    read -r RESPONSE

    if [[ "$RESPONSE" =~ ^[Yy]$ ]]; then
        sudo certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos -m ${EMAIL} --redirect

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ SSL 인증서 발급 완료!${NC}"
            echo ""
            echo -e "${GREEN}=================================="
            echo -e "🎉 모든 설정 완료!"
            echo -e "==================================${NC}"
            echo ""
            echo "API 접속: https://${DOMAIN}"
            echo "Swagger UI: https://${DOMAIN}/docs"
            echo ""
            echo -e "${YELLOW}다음 단계:${NC}"
            echo "1. Vercel 프론트엔드에 백엔드 URL 설정"
            echo "2. 정기 백업 스크립트 설정 (선택사항)"
        else
            echo -e "${RED}❌ SSL 인증서 발급 실패${NC}"
            echo "도메인의 DNS 설정을 확인하세요."
            exit 1
        fi
    else
        echo -e "${GREEN}✅ Nginx 설정 완료!${NC}"
        echo "API 접속: http://${DOMAIN}"
    fi
fi

echo ""
echo -e "${YELLOW}유용한 명령어:${NC}"
echo "서비스 상태: sudo systemctl status xperion-wiki"
echo "로그 확인: sudo journalctl -u xperion-wiki -f"
echo "Nginx 로그: sudo tail -f /var/log/nginx/xperion-wiki-error.log"
echo "서비스 재시작: sudo systemctl restart xperion-wiki"
