# VeyaShip - Frontend Production Dockerfile
# 多阶段构建：Node 构建 → Nginx 运行
# 用于 docker-compose.prod.yml 构建生产镜像

# ════════════════════════════════════════════════════════════════
# 第一阶段：构建前端
# ════════════════════════════════════════════════════════════════
FROM node:20-alpine AS build

WORKDIR /app

# 先拷依赖文件，用缓存加速
COPY package.json package-lock.json* ./
# 如果有 package-lock.json 用 npm ci（更快更精确），否则用 npm install
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# 复制源码并构建
COPY . .
RUN npm run build

# ════════════════════════════════════════════════════════════════
# 第二阶段：Nginx 运行
# ════════════════════════════════════════════════════════════════
FROM nginx:1.25-alpine AS production

# 从 build 阶段复制构建产物
COPY --from=build /app/dist /usr/share/nginx/html
# 覆盖 Nginx 默认配置（SPA fallback + Gzip + 安全头）
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
