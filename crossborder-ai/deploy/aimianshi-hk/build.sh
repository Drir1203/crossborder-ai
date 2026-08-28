#!/usr/bin/env bash
# AI 面师（interview-coach）香港部署 — 依赖安装 + 构建
# 以 ubuntu 身份在 /opt/interview-coach 执行
set -e
cd /opt/interview-coach

echo "==> 同步代码到 origin/main"
git fetch origin main 2>&1 | tail -2 || echo "(fetch 提示忽略)"
git reset --hard origin/main 2>&1 | tail -1
echo "HEAD=$(git rev-parse --short HEAD)"

echo "==> npm install --ignore-scripts (npmmirror 镜像)"
npm install --ignore-scripts --registry=https://registry.npmmirror.com 2>&1 | tail -6

echo "==> 补齐 ffmpeg-static 二进制 (HK 网络直连 GitHub)"
(node node_modules/ffmpeg-static/install.js && echo "ffmpeg-static OK") || echo "ffmpeg-static 下载失败(可后续补)"

echo "==> prisma generate"
npx prisma generate 2>&1 | tail -3

echo "==> prisma db push (同步 schema)"
npx prisma db push 2>&1 | tail -6 || echo "(db push 输出有告警，运行时再验证)"

echo "==> npm run build"
npm run build 2>&1 | tail -40

echo "BUILD_DONE"
