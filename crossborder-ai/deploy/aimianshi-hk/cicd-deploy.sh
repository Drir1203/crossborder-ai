#!/bin/bash
set -euo pipefail

cd /opt/interview-coach

# ① 备份服务器本地配置（git reset 可能误删）
cp ecosystem.config.cjs /tmp/ecosystem.bak 2>/dev/null || true
cp .env /tmp/env.bak 2>/dev/null || true

# ② 同步代码：服务器 = GitHub main 镜像（带重试）
for i in 1 2 3 4 5; do
  git fetch origin main && git reset --hard origin/main && break
  sleep 5
done

# ③ 恢复本地配置（若被 reset 误删）
[ -f ecosystem.config.cjs ] || cp /tmp/ecosystem.bak ecosystem.config.cjs 2>/dev/null || true
[ -f .env ] || cp /tmp/env.bak .env 2>/dev/null || true

# ④ 清理陈旧 pm2 条目（防 start 失败），再停服
pm2 delete i面试 2>/dev/null || true

# ⑤ 数据库
npx prisma db push --accept-data-loss 2>&1 | tail -1
npx prisma generate 2>&1 | grep Generated

# ⑥ 依赖 + 构建（--ignore-scripts 防 ffmpeg 超时）
npm install --ignore-scripts 2>&1 | tail -1
npm run build 2>&1 | grep -E "error|Compiled" | head -1

# ⑦ 从配置启动（健壮，不依赖 pm2 既有条目）
pm2 start ecosystem.config.cjs
pm2 save

# ⑧ 健康检查
sleep 4
curl -sfL -o /dev/null -w "panel %{http_code}\n" http://127.0.0.1:3000/interview/ || exit 1
echo "✅ 部署完成"
