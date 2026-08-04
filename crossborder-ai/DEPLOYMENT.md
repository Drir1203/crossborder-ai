# VeyaShip 生产部署方案

> 更新时间：2026-08-04
> 面向：全栈岗位面试可讲的完整部署架构说明
>
> 本文档覆盖：系统架构 → 生产部署现状 → CI/CD 自动部署流水线 → 关键技术决策 → 安全性 → 故障排查与回滚 → 面试可深挖的话题

---

## 一、系统架构总览

```
用户浏览器
    │  HTTPS (veyaship.com)
    ▼
┌─────────────┐
│    Nginx    │  Web 服务器：SSL 终止 / 静态资源 / 反向代理
└──────┬──────┘
       │ 静态前端                 │ /api/* 反向代理        │ /interview/*
       ▼                          ▼                        ▼
┌─────────────┐        ┌──────────────────┐      ┌────────────────┐
│ 前端静态文件 │        │   FastAPI 后端    │      │  interview 项目 │
│ /var/www/   │        │  uvicorn×4 worker│      │  Next.js :3000 │
│ veyaship    │        │  :8000           │      └────────────────┘
└─────────────┘        └────────┬─────────┘
                                │ SQLAlchemy(async)
                                ▼
                       ┌──────────────────┐
                       │  PostgreSQL 16    │
                       │  原生 systemd 管理 │
                       └──────────────────┘
```

- **前端**：React 18 + Vite + TypeScript，构建产物为纯静态文件（js/css/html）
- **后端**：Python FastAPI + SQLAlchemy 2.0 异步，uvicorn 4 个 worker 进程
- **数据库**：PostgreSQL 16（服务器原生安装，systemd 管理）
- **Web 层**：Nginx 统一入口 —— SSL 证书终止、静态资源托管、`/api` 反向代理到后端
- **AI 服务**：DeepSeek（文本）、阿里云通义万相（图片，Replicate FLUX 降级）—— 均为外部 API，后端作为聚合层

---

## 二、生产部署现状（服务器视角）

| 项 | 说明 |
|----|------|
| 服务器 | 阿里云 ECS 2核2G / Ubuntu 24.04，公网 IP `47.116.138.61` |
| 域名 | `https://veyaship.com`（HTTPS，Let's Encrypt 证书 + 自动续期） |
| 代码位置 | `/opt/veyaship`（git 仓库，服务器是 GitHub main 的镜像） |
| 后端运行 | systemd 服务 `veyaship-backend.service`：`uvicorn app.main:app --workers 4` |
| 前端发布 | 构建产物复制到 `/var/www/veyaship/`，Nginx 静态托管 |
| 数据库 | PostgreSQL 16（原生安装），后端启动时 `create_all` 自动建表 |
| 环境变量 | `/opt/veyaship/.../.env`（含密钥），不入 git，不被 CI 覆盖 |

**systemd 服务单元（veyaship-backend.service）核心配置：**

```ini
[Service]
Type=simple
WorkingDirectory=/opt/veyaship/crossborder-ai/backend
ExecStart=/opt/veyaship/crossborder-ai/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always        # 崩溃自动拉起
RestartSec=5
```

**Nginx 关键配置：**

```nginx
location / {            root /var/www/veyaship; try_files $uri $uri/ /index.html; }  # SPA 路由
location /api/ {        proxy_pass http://localhost:8000; }                         # 后端反向代理
location /health {      proxy_pass http://localhost:8000/health; }                  # 健康检查
location /assets/ {     root /var/www/veyaship; expires 1y; }                       # 静态资源长缓存
```

---

## 三、CI/CD 自动部署流水线（核心亮点）

### 流程图

```
开发者 git push 到 main
        │
        ▼
┌─────────────────────────────┐
│  GitHub Actions 自动触发     │
│  .github/workflows/deploy.yml│
│  runs-on: ubuntu-latest     │
└─────────────┬───────────────┘
              │ appleboy/ssh-action（SSH 连接）
              │ 用 Secrets 里存的 CI 专用密钥
              ▼
┌─────────────────────────────┐
│  生产服务器执行 cicd-deploy.sh│
│  ① git fetch + reset（同步代码）│
│  ② pip install（后端依赖）    │
│  ③ npm ci + vite build（前端）│
│  ④ cp 构建产物 → nginx 目录   │
│  ⑤ systemctl restart 后端    │
│  ⑥ 健康检查（最多等 120s）    │
└─────────────────────────────┘
              │
              ▼
        部署完成 ✅
```

### 工作流文件（`.github/workflows/deploy.yml`）

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:          # 支持手动触发

jobs:
  deploy:
    name: 部署到生产服务器
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - name: SSH 执行服务器部署脚本
        uses: appleboy/ssh-action@v1.2.0
        with:
          host: ${{ secrets.VEYASHIP_HOST }}
          username: root
          key: ${{ secrets.VEYASHIP_SSH_KEY }}
          script: |
            set -e
            bash /opt/veyaship/cicd-deploy.sh
```

### 部署脚本（`/opt/veyaship/cicd-deploy.sh`）核心逻辑

```bash
set -euo pipefail   # 出错即停，杜绝"半部署"状态

# ① 同步代码：服务器 = GitHub main 的镜像（带网络重试，抗 GitHub 抖动）
for i in 1 2 3 4 5; do
  git fetch origin main && git reset --hard origin/main && break
  sleep 5
done

# ② 后端依赖
cd /opt/veyaship/crossborder-ai/backend
./venv/bin/pip install -r requirements.txt

# ③ 前端构建（npm ci 保证依赖可复现）
cd /opt/veyaship/crossborder-ai/frontend
npm ci --no-audit --no-fund
npm run build        # vite build

# ④ 发布前端：先清空再复制，避免残留旧文件
rm -rf /var/www/veyaship/*
cp -r dist/* /var/www/veyaship/

# ⑤ 重启后端
systemctl restart veyaship-backend.service

# ⑥ 健康检查：服务器启动慢，最多等 120s，确保部署成功才报"完成"
for i in 1 2 3 4 5 6 7 8 9 10 11 12; do
  sleep 10
  curl -sf http://localhost:8000/health && exit 0
done
exit 1   # 120s 内后端没起来 → 部署失败，CI 标红
```

### 使用的 Secrets

| Secret | 说明 |
|--------|------|
| `VEYASHIP_HOST` | 服务器公网 IP（47.116.138.61） |
| `VEYASHIP_SSH_KEY` | **CI 专用** ED25519 私钥（`~/.ssh/veyaship_ci`，已加入服务器 authorized_keys） |

> GitHub 的 Secrets 用 libsodium 密封加密存储，只有 Actions 运行时可读，不会出现在日志里。

---

## 四、关键技术决策与权衡（面试重点）

### 1. 为什么用 GitHub Actions 而不是 Jenkins / 其他 CI？

- **零成本、零运维**：GitHub 自带，public repo 免费，无需自建 CI 服务器
- **天然集成**：push 事件直接触发，不需要额外 webhook 配置
- **声明式 YAML**：工作流即代码，随仓库版本管理
- **生态成熟**：`appleboy/ssh-action` 这类官方/社区 action 开箱即用

### 2. 为什么服务器直接跑 systemd + Nginx，而不是 Docker 化？

仓库里其实**已经准备了 `docker-compose.prod.yml`**（postgres/backend/frontend/nginx 全容器化），但生产选择了 systemd + 原生服务。权衡：

| 维度 | systemd + Nginx（当前） | Docker Compose |
|------|----------------------|----------------|
| 部署速度 | 快（改一行重启即生效） | 需构建镜像，较慢 |
| 资源占用 | 低，无容器层 | 有镜像/网络开销 |
| 隔离性 | 弱（依赖系统环境） | 强，环境可复现 |
| 回滚 | git reset + 重启 | docker tag 切换 |
| 适合场景 | 单机、资源紧张、快速迭代 | 多机、需要环境一致、上规模后 |

**决策依据**：单台 2C2G 小服务器、单项目、快速迭代阶段，systemd 最简单可靠；Docker 化已备好，作为上规模后的演进方向。**这个"先简单后演进"的思路本身也是面试加分点。**

### 3. 为什么用「SSH + git pull」而不是「推送镜像到容器仓库」？

- 单台服务器，SSH + git pull 是最短路径，无中间镜像仓库
- 服务器是 git 镜像，天然保留了完整版本历史，回滚只需 `git reset` 到历史提交
- 如果未来多台服务器，再演进为「CI 构建镜像 → push 到 GHCR → 服务器 pull」

### 4. 构建可靠性处理

- **`npm run build` 改为 `vite build`**：项目历史遗留的 `tsc -b` 步骤因 tsconfig 配置冲突（TS6310）+ 历史类型错误一直构建失败，vite（esbuild）只转译不类型检查，保证构建稳定；类型错误单独列为技术债清理
- **`npm ci` 而非 `npm install`**：按 lockfile 精确安装，构建可复现
- **健康检查 + 超时**：后端 4 个 worker 并发启动时 init_db 较慢，健康检查等 120s，避免"部署成功但服务没起来"的假象

---

## 五、安全性

1. **SSH 密钥分级**：日常运维用一把密钥，CI 用**独立的专用密钥**（`veyaship_ci`），互不影响；私钥只存在于开发者本机 + GitHub Secrets，**绝不提交到 git**
2. **Secrets 加密存储**：GitHub Actions Secrets 用 libsodium 密封加密，Actions 日志自动打码，密钥不会泄露
3. **.env 不入库**：数据库密码、JWT 密钥、API Key 都在服务器 `.env`，git 忽略，CI 部署不覆盖
4. **SSL 终止**：HTTPS 在 Nginx 层统一处理（Let's Encrypt + 自动续期）
5. **后端鉴权**：JWT（access + refresh），接口按功能做积分/套餐权限控制

---

## 六、故障排查与回滚

### 常见故障

| 症状 | 排查 | 处理 |
|------|------|------|
| CI 标红 | 看 Actions 运行日志 | 看是 SSH 连接失败、脚本报错还是健康检查超时 |
| 后端 500 | `journalctl -u veyaship-backend.service` 看 traceback | 定位代码问题，修复后重新部署 |
| 前端白屏 | 看浏览器 console + 确认 `/var/www/veyaship` 有构建产物 | 重新 `vite build` 或回滚 |
| 部署中断 | `set -e` 保证不会半部署，旧版本保持可服务 | 重跑部署脚本 |

### 回滚流程（发布新版本出问题时的应急预案）

```bash
# 1. 在服务器上找到上一个正常版本的提交号
cd /opt/veyaship
git log --oneline -5

# 2. 回滚代码 + 重新部署（复用同一套脚本，只是代码不同）
git reset --hard <上一个正常commit>
bash /opt/veyaship/cicd-deploy.sh   # 或用 CI 重新跑
```

> 回滚的本质：**服务器是 git 镜像，所以回滚 = 切代码版本 + 重跑同一套部署**。这比容器 tag 回滚更直观。

---

## 七、面试可深挖的话题

1. **"如何保证部署可回滚？"** → 服务器是 git 镜像，`git reset` + 重跑部署脚本；未来 Docker 化后是镜像 tag 切换
2. **"CI 里怎么安全存凭据？"** → GitHub Actions Secrets 加密存储，SSH 专用密钥，绝不打进日志
3. **"部署过程中如果服务挂了怎么办？"** → `set -e` 原子化 + 健康检查门槛 + systemd `Restart=always` 自动拉起
4. **"为什么不在 CI 里构建镜像？"** → 单机场景 SSH + git 最短路径；多机再演进到镜像仓库
5. **"如何保证构建可复现？"** → `npm ci`（lockfile）、pip 依赖锁定、vite 确定性构建
6. **"服务器网络抖动怎么处理？"** → git fetch 自动重试；这在国内访问 GitHub 是真实痛点
7. **"监控怎么做？"** → 现状：Nginx + 后端健康检查 + CI 状态；可演进：Prometheus + Grafana / Sentry

---

## 八、如何把这套方案讲给面试官（叙事模板）

> **一句话**：这是一个"单人 + 单台云服务器 + 全栈项目"场景下，兼顾速度、可靠性和可演进的部署方案。

> **展开**：我从 0 到 1 搭过生产环境 —— 服务器装 Nginx + PostgreSQL + Python 环境，域名 + HTTPS 证书，后端做成 systemd 服务保证崩溃自愈，前端构建成静态文件交给 Nginx 托管。后来手动部署太痛苦（要 SSH 上去拉代码、重启、容易出错），就上了 GitHub Actions：**push 代码 → CI 自动 SSH 到服务器 → 拉代码、装依赖、构建前端、重启后端、健康检查**，一条流水线跑完，部署从"半小时手动操作"变成"push 即自动"。密钥走 GitHub Secrets 加密，还做了独立 CI 密钥。遇到服务器连 GitHub 网络抖动、后端启动慢这类真实问题，也都用重试和超时机制解决掉了。

> **主动拔高**：我知道现在这套是单机最简方案，也准备好了演进路径 —— 仓库里已经写了 docker-compose 配置，等业务上规模就切容器化 + 镜像仓库；监控也可以接 Prometheus。先解决 0→1 的问题，再考虑规模化的优雅。
