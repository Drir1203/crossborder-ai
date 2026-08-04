# VeyaShip 生产部署清单

> 每个步骤标注了自动化程度：
>
> - **🤖 自动** — 我已经写好脚本/代码，**你只需执行我给的命令**
> - **🔧 半自动** — 我能生成模板/脚本，但需要你提供信息后触发
> - **👤 必须手动** — 得你自己操作（买买买、注册账号、点按钮）

---

## 快速入门（3 步上线）

你只需要做 **3 件事**，剩下的我可以自动化或已有脚本：

```
👤 1. 买个服务器 + 把域名指向它（~10 分钟）
👤 2. 注册 DeepSeek + 阿里云通义万相拿到 API Key（~5 分钟）
🤖 3. 运行我给你的 3 条命令（~3 分钟）
```

---

## 详细清单

### 1️⃣ 前置准备

#### 1.1 买服务器

| 步骤 | 自动化 | 说明 |
|------|--------|------|
| 购买 VPS | 👤 **手动** | 推荐 DigitalOcean 2核4G ($12/月) 或 阿里云轻量 (¥68/月) |
| 记下服务器 IP | 👤 **手动** | 买完后控制台会显示 IP |
| 告诉我 IP 和密码 | 👤 **手动** | 后续脚本需要连服务器 |

**我能做什么**：🤖 等你告诉我服务器 IP 后，我能直接 SSH 上去帮你初始化。

#### 1.2 域名 DNS

| 步骤 | 自动化 | 说明 |
|------|--------|------|
| 域名 DNS 解析指向服务器 IP | 👤 **手动** | 在你域名的 DNS 管理后台加 A 记录 |

**我能做什么**：DNS 解析我帮不了，得你自己去域名管理面板操作。

#### 1.3 申请 API Key

| 步骤 | 自动化 | 说明 |
|------|--------|------|
| DeepSeek API Key | 👤 **手动** | https://platform.deepseek.com/api_keys |
| 阿里云通义万相 API Key | 👤 **手动** | https://dashscope.console.aliyun.com/api-key |
| Replicate API Key（可选降级） | 👤 **手动** | https://replicate.com/account/api-tokens |

**我能做什么**：🤖 你拿到 Key 后告诉我，我帮你填到配置文件里。

---

### 2️⃣ 服务器初始化（我给你命令，你复制粘贴）

这一步开始，**大部分工作我已经写成脚本了**，你只需要复制运行我给的命令。

#### 2.1 连接服务器

```bash
# 👤 你运行这个（改成你的 IP）
ssh root@你的服务器IP
```

#### 2.2 安装 Docker

```bash
# 🤖 一条命令装完
curl -fsSL https://get.docker.com | bash
```

#### 2.3 获取代码

```bash
# 🤖 方案 A：GitHub（推荐，方便后续更新）
# 👤 你需要在 GitHub 建个私有仓库，然后我帮你把代码推上去
# 然后你在服务器上：
git clone https://github.com/你的用户名/crossborder-ai.git /opt/veyaship

# 🔧 方案 B：我帮你打包，你上传
# 我可以在这里把代码打成 tar.gz，你下载后用 scp 传上去
```

**我能做什么**：
- 🤖 如果你有 GitHub 仓库，我直接帮你 `git push`
- 🔧 我可以帮你生成一个 deployment.zip 包
- 🤖 `deploy.sh` 脚本已经写好了放在项目根目录

#### 2.4 运一键部署脚本

```bash
# 🔧 先编辑环境变量
cd /opt/veyaship
nano .env
# 填入以下信息（其他字段脚本已自动生成）：
#   1. POSTGRES_PASSWORD = 你设置一个强密码
#   2. DEEPSEEK_API_KEY = sk-xxx
#   3. REPLICATE_API_KEY = r8_xxx
#   4. APP_URL = https://你的域名.com
#   5. BACKEND_CORS_ORIGINS = ["https://你的域名.com"]

# ⚠️ 保存退出后，运行：
sudo ./deploy.sh
```

**我能做什么**：
- 🤖 我已经写好了 `deploy.sh`，它会自动完成：
  - 安装 Docker（如果未装）
  - 生成随机 SECRET_KEY / JWT_SECRET_KEY
  - 申请 Let's Encrypt SSL 证书
  - 构建 Docker 镜像
  - 启动 PostgreSQL + Qdrant + 后端 + 前端 + Nginx
  - 初始化数据库表
  - 健康检查

---

### 3️⃣ 所有自动化资源汇总

以下所有文件 **我已经写好存在项目里**，你不需要自己写任何脚本：

| 文件 | 作用 | 谁写的 |
|------|------|--------|
| `deploy.sh` | 一键部署脚本（安装 Docker → 构建 → 启动 → 检查） | ✅ 我 |
| `docker-compose.prod.yml` | 生产环境容器编排（6 个服务 + 资源限制 + 健康检查） | ✅ 我 |
| `backend/Dockerfile` | Python 3.12 多阶段构建镜像 | ✅ 我 |
| `frontend/Dockerfile` | Node 20 构建 → Nginx 运行 | ✅ 我 |
| `nginx/nginx.conf` | HTTPS + 安全头 + Certbot + SPA fallback | ✅ 我 |
| `.env.production` | 环境变量模板（含所有注释说明） | ✅ 我 |
| `backend/.dockerignore` | 防止 .env/DB 打包进镜像 | ✅ 我 |
| `frontend/.dockerignore` | 防止 node_modules 打包进镜像 | ✅ 我 |
| `backend/migrations/env.py` | Alembic 迁移环境（自动读 .env 配置） | ✅ 我 |
| `backend/migrations/versions/003_create_all_tables.py` | 全量数据库迁移（11 张表） | ✅ 我 |
| `backend/requirements.txt` | +psycopg2-binary 支持 Alembic | ✅ 我 |
| `.gitignore` | 优化环境文件规则 | ✅ 我 |
| `README.md` | 部署章节已更新 | ✅ 我 |

---

### 4️⃣ 还需要你手动做的事

| # | 事项 | 预计时间 | 说明 |
|---|------|---------|------|
| 1 | **买服务器** | 5 分钟 | 选 DigitalOcean / 阿里云 / Vultr |
| 2 | **域名 DNS 解析** | 5 分钟 | A 记录指向服务器 IP |
| 3 | **注册 DeepSeek** | 3 分钟 | https://platform.deepseek.com |
| 4 | **注册阿里云通义万相** | 3 分钟 | https://dashscope.console.aliyun.com/ |
| 5 | **SSH 连接服务器** | 2 分钟 | `ssh root@你的IP` |
| 6 | **配置 .env 中的个人信息** | 3 分钟 | 填入 API Key + 域名 |
| 7 | **验收测试** | 10 分钟 | 按第 9 节测试所有功能 |

**总计：约 30 分钟**，其中实际你操作的时间约 10 分钟，剩下的都是等脚本执行。

---

### 5️⃣ 我能帮你进一步自动化的

只要你有以下信息，我可以 **直接在这聊天框里帮你完成**：

| 信息 | 我能做什么 |
|------|-----------|
| 你的 GitHub 用户名 | 🤖 帮你初始化 git、创建 commit、推送到 GitHub |
| 你的服务器 IP + 密码/SSH Key | 🤖 直接 SSH 上去运行部署脚本 |
| 你的 API Key | 🤖 帮你生成完整的 `.env` 文件 |
| 你的域名 | 🤖 帮你替换 nginx.conf 中的 example.com |

---

### 6️⃣ 最终执行流程（剪掉所有废话）

```
你                               我
│                                 │
├─ 1. 买服务器 ──────────────────→│
│                                 │
├─ 2. 告诉我服务器 IP + 密码 ───→│
│                                 ├─ 3. SSH 登录服务器
│                                 ├─ 4. 安装 Docker
│                                 ├─ 5. 部署代码
│                                 ├─ 6. 生成 .env（等你填 Key）
│◄────────────────────────────────┤
│                                 │
├─ 7. 告诉我 API Key + 域名 ────→│
│                                 ├─ 8. 填入 .env
│                                 ├─ 9. 运行 deploy.sh
│                                 ├─10. SSL 证书
│                                 ├─11. 构建 + 启动
│                                 ├─12. 健康检查
│◄────────────────────────────────┤
│                                 │
├─ 13. 验收 ✅ 上线 │
│                                 │
```

---

### 7️⃣ 直接从这里开始

如果你现在就想开始，**回复我以下信息**：

```
1. 服务器 IP：________
2. 登录密码 或 SSH Key：________
3. 域名：________
4. DeepSeek API Key：________
5. 阿里云通义万相 API Key：________
```

我就可以**直接 SSH 连上服务器，把剩下所有事情自动化完成**。

或者你也可以先自己买服务器、注册账号，搞定了告诉我，我从第 2 步开始。
