#!/usr/bin/env bash
# mianshi.pro 香港 — nginx + certbot 上线脚本
# 前置条件：DNS 已生效（HK 服务器上 dig mianshi.pro 能解析到 43.129.23.197）
# 在 HK 以 ubuntu 身份执行一次
set -e
DOMAIN=mianshi.pro
SRV=/etc/nginx/sites-available/$DOMAIN
ENL=/etc/nginx/sites-enabled/$DOMAIN

sudo mkdir -p /var/www/html

echo "==> 阶段1：仅 80 端口（供 ACME 验证）"
sudo tee $SRV >/dev/null <<NGINX
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    location /.well-known/acme-challenge/ { root /var/www/html; }
    location / { return 301 https://\$host\$request_uri; }
}
NGINX
sudo ln -sf $SRV $ENL
sudo nginx -t && sudo systemctl reload nginx
echo "phase1 ok"

echo "==> 阶段2：certbot 签证书"
sudo certbot certonly --webroot -w /var/www/html -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --no-eff-email
echo "cert ok"

echo "==> 阶段3：完整配置（80 + 443，根路径→/interview/）"
sudo tee $SRV >/dev/null <<NGINX
server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    ssl_certificate     /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    client_max_body_size 200m;
    location = / { return 308 /interview/; }
    location /interview {
        add_header Cache-Control "no-store";
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    location /.well-known/acme-challenge/ { root /var/www/html; }
    location / { return 301 https://\$host\$request_uri; }
}
NGINX
sudo nginx -t && sudo systemctl reload nginx
echo "NGINX_DONE"
