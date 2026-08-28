#!/usr/bin/env bash
# AI 面师（interview-coach）香港迁移 — 数据库落地脚本
# 在腾讯云香港服务器上以 ubuntu 身份执行（sudo 免密）
# 依赖前置：/tmp/aimianshi.dump 与 /tmp/aimianshi.env 已就位
set -e
cd /opt/interview-coach

echo "==> 放置 .env"
sudo mv -f /tmp/aimianshi.env .env
sudo chown ubuntu:ubuntu .env

echo "==> 替换 AUTH_URL 为 mianshi.pro（脱敏展示）"
sed -i 's#https://47.116.138.61#https://mianshi.pro#g' .env
grep -E '^(NEXTAUTH_URL|AUTH_URL|DATABASE_URL)=' .env | sed -E 's#(://[^:]+):[^@]+@#\1:***@#'

echo "==> 解析数据库凭据"
DATABASE_URL=$(grep -E '^DATABASE_URL=' .env | cut -d= -f2- | tr -d '"')
U=$(echo "$DATABASE_URL" | sed -E 's#postgresql://([^:]+):.*#\1#')
PW=$(echo "$DATABASE_URL" | sed -E 's#postgresql://[^:]+:([^@]+)@.*#\1#')
DB=$(echo "$DATABASE_URL" | sed -E 's#.*/([^?]+)\?.*#\1#')
echo "user=$U db=$DB (密码不显示)"

echo "==> 创建 PG 角色与库"
sudo -u postgres psql -v ON_ERROR_STOP=0 <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='$U') THEN
    CREATE ROLE $U LOGIN PASSWORD '$PW';
  ELSE
    ALTER ROLE $U WITH LOGIN PASSWORD '$PW';
  END IF;
END
\$\$;
SQL
sudo -u postgres createdb -O "$U" "$DB" 2>/dev/null && echo "db created" || echo "db exists"

echo "==> 恢复数据"
pg_restore -Fc -d "$DATABASE_URL" /tmp/aimianshi.dump
echo "RESTORE_OK"

echo "==> 表清单"
psql "$DATABASE_URL" -c '\dt' | head -40
