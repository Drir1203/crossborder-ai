# VeyaShip 生产部署完成备忘

> 上线日期：2026-07-24
> 服务器：阿里云轻量 2核2G | Ubuntu 24.04 | 47.116.138.61
> 域名：https://veyaship.com
> GitHub：https://github.com/Drir1203/crossborder-ai

---

## 一、访问地址

| 入口 | 地址 |
|------|------|
| 前端首页 | **https://veyaship.com** |
| API 接口 | **https://veyaship.com/api/v1** |
| 健康检查 | **https://veyaship.com/health** |
| 服务器 IP | 47.116.138.61 |

---

## 二、后续需要做的事

### □ 1. ICP 备案（国内服务器必需）
阿里云国内服务器必须备案，否则 80/443 端口可能被拦截。
```
阿里云控制台 → ICP 备案 → 开始备案
预计 7-20 天
```

### □ 2. 注册第一个用户验收
```
访问 https://veyaship.com → 注册账号
测试完整流程：
  □ 注册/登录
  □ 手动录入商品（产品页）
  □ AI 生成 Listing（内容页）
  □ 净利计算（财务页）
  □ Dashboard 看板
```

### □ 3. 配置 Onebound API Key（1688 抓取）
在设置页面配置，否则抓取 1688 商品会失败。
```
登录后 → 设置 → 爬虫配置 → 填入 API Key
```

### □ 4. 配置 Shopify API Key（如需 Shopify 功能）
```
Shopify 功能需要：
1. 在 Shopify Partners 后台创建应用
2. 获取 API Key + API Secret
3. 在 .env 中配置后重启后端
```

---

## 三、常用运维命令

### SSH 连接
```bash
ssh -i ~/.ssh/deploy_key root@47.116.138.61
```

### 查看日志
```bash
# 后端日志（实时）
journalctl -u veyaship-backend -f

# Nginx 访问日志
tail -f /var/log/nginx/access.log

# Nginx 错误日志
tail -f /var/log/nginx/error.log
```

### 服务管理
```bash
# 重启后端
systemctl restart veyaship-backend

# 查看后端状态
systemctl status veyaship-backend

# 重启 Nginx
systemctl restart nginx

# 查看 Nginx 配置是否正确
nginx -t
```

### 数据库
```bash
# 手动备份
pg_dump -U postgres crossborder_ai > /opt/backups/veyaship_$(date +%Y%m%d).sql

# 恢复备份
psql -U postgres crossborder_ai < /opt/backups/veyaship_20260724.sql

# 进入数据库交互
psql -U postgres crossborder_ai
```

### 更新代码
```bash
cd /opt/veyaship/crossborder-ai

# 拉取最新代码
git pull

# 安装新依赖
cd backend && source venv/bin/activate
pip install -r requirements.txt -q

# 重启后端
systemctl restart veyaship-backend

# 如果前端有更新
cd /opt/veyaship/crossborder-ai/frontend
npm install && npx vite build
cp -r dist/* /var/www/veyaship/
```

### SSL 证书
```bash
# 手动续期（证书有效期 90 天，cron 自动续期）
certbot renew

# 查看证书到期时间
certbot certificates
```

### 磁盘 & 资源
```bash
# 磁盘使用
df -h /

# 内存使用
free -h

# Docker 资源（如果将来切回 Docker 部署）
docker stats
```

### 故障排查
```bash
# 后端挂了
systemctl status veyaship-backend
journalctl -u veyaship-backend -n 50 --no-pager

# API 不通
curl -s http://localhost:8000/health

# Nginx 配置有问题
nginx -t

# 数据库连不上
pg_isready -U postgres

# 502 Bad Gateway
# → 检查后端是否运行：systemctl status veyaship-backend
# → 检查端口：ss -tlnp | grep 8000
```

---

## 四、部署架构

```
用户浏览器
    ↓ HTTPS
Nginx（反向代理 + 静态文件）
    ↓                ↓
  /api/*           / → /var/www/veyaship/（前端 SPA）
  localhost:8000
    ↓
uvicorn（4 workers）
    ↓
PostgreSQL（本地 5432 端口）
```

## 五、相关文件位置

| 文件 | 路径 |
|------|------|
| 后端代码 | `/opt/veyaship/crossborder-ai/backend/` |
| 前端构建产物 | `/var/www/veyaship/` |
| 后端日志 | `journalctl -u veyaship-backend` |
| Nginx 站点配置 | `/etc/nginx/sites-enabled/veyaship.conf` |
| systemd 服务文件 | `/etc/systemd/system/veyaship-backend.service` |
| 环境变量 | `/opt/veyaship/crossborder-ai/.env` |
| Python 虚拟环境 | `/opt/veyaship/crossborder-ai/backend/venv/` |

## 六、切换回 Docker 部署（接入 VPN 后）

```bash
# 1. 停止当前服务
systemctl stop veyaship-backend nginx

# 2. 确认 Docker 可用
docker --version

# 3. 一行命令启动所有服务
cd /opt/veyaship/crossborder-ai
docker compose -f docker-compose.prod.yml up -d --build

# 4. 检查
curl -s https://veyaship.com/health
```
