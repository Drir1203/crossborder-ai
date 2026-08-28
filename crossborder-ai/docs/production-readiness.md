# VeyaShip 商业化生产就绪度评估

> 日期：2026-08-26
> 范围：对当前代码库（FastAPI 后端 + React 前端）面向商业化生产的能力盘点。
> 方法：所有结论均对照真实代码核实，附 `文件:行号` 证据；标注 ✅ 问题成立、部分成立时说明程度。

---

## 结论摘要

代码层面（任务队列、可观测性、限流）的问题属于「能跑但扛不住」；更严重的是本轮发现的三个**「商业化根本没法开始」**问题：

1. **支付闭环是断的** —— 收款 / 验签 / 开通三段全是占位
2. **安全基线有真漏洞** —— SSRF、服务商 API Key 明文、JWT 空密钥不拒启
3. **无备份机制** —— 单机单点，数据丢失不可逆

一句话：前者决定你能撑多大用户量，后者决定你能不能收第一笔钱。

> 2026-08-27 更新：上述 P0/P1 问题已全部修复（见下「✅ 修复进度」表）；当前待办收敛为 P2 体验优化（流式输出 / ErrorBoundary）与自动收款（Creem 验签，刻意后置）。

---

## ✅ 修复进度（2026-08-27 更新）

按「先数据安全 → 再可靠性 → 最后体验」顺序逐项修复，每项均经 pytest + 真实服务器冒烟验证：

| 项 | 等级 | 状态 | 落地说明 |
|----|------|------|----------|
| 1. 支付闭环 | P0 | ✅ **人工闭环已上线** | 申请落库 → 转账 → 管理员一键开通/拒绝 → 对账，全链路可运营（见下节）；**自动收款 + Creem 验签刻意后置** |
| 2. 安全基线 | P0 | ✅ 已修 | SSRF IP 校验（拒私网/环回/元数据）、API Key Fernet 加密 + 掩码回显、JWT 空密钥拒启 |
| 3. 无备份 | P0 | ✅ 已修 | [deploy/backup.sh](../deploy/backup.sh) 数据库定时备份 |
| 4. 任务队列 + 幂等 | P1 | ✅ 已修 | Agent 异步任务状态机 + Idempotency-Key + 僵尸恢复 + 成功才扣积分 |
| 5. 可观测性 | P1 | ✅ 已修 | Sentry（sentry-sdk）+ 请求链路 ID |
| 6. 限流 + 修 500 | P1 | ✅ 已修 | 内存限流改数据库窗口计数（PG），并发 500 修复；**Redis 化可后置** |
| 7. 迁移部署 | P1 | ✅ 已修 | Alembic 迁移 + 启动 create_all 防呆 + deploy 脚本梳理 |
| 8. 分布式定时 | P2 | ✅ 已修 | PG advisory lock 跨进程防重，5 个 job 全包裹 |
| 9. 流式输出 | P2 | ⏳ 待做（纯体验优化） | 需 SSE 基建：任务执行时推流，异步轮询已就位，可后置 |
| 10. 前端健壮性 | P2 | ✅ 已修 | 顶层 ErrorBoundary（[ErrorBoundary.tsx](../frontend/src/components/common/ErrorBoundary.tsx)）防 LLM 字段漂移白屏 |

---

## P0 —— 商业化命门（不修不能收费上线）

### 1. 支付闭环：收钱的路是断的 🚨

当前支付 = **手动转账 + 客服手动开权限**：

- 前端调的 `POST /billing/upgrade`（[backend/app/routers/billing.py:58](backend/app/routers/billing.py#L58)）返回「请转账 ¥xxx 到支付宝/微信，备注订单号，加客服微信手动处理」
- `POST /billing/verify`（[backend/app/routers/billing.py:90](backend/app/routers/billing.py#L90)）直接返回「请联系客服手动升级」，注释自认「**生产环境应接入自动支付回调**」
- 真正的支付集成（Creem.io）写在 [backend/app/services/payment.py](backend/app/services/payment.py) 和 [backend/app/api/v1/endpoints/payments.py](backend/app/api/v1/endpoints/payments.py)，但 **payments.py 未挂载** —— main.py 的 13 个 `include_router` 里没有它，是死代码

webhook 处理是空壳：

```python
# payment.py:85-93 —— 验签是注释掉的 TODO，直接 return True
# TODO: Implement HMAC verification with CREEM_WEBHOOK_SECRET
return True

# payments.py:174-179 —— 业务逻辑全是 pass
if event_type == "payment.succeeded":
    pass   # ← 不升级、不发积分
```

**影响**：即使接入 Creem，用户付了钱也不会自动拿到套餐。收款 → 验签 → 开通三段全占位。

**如果是有意用手动收款启动**（客服微信收钱、手动改 plan），当前代码能跑，但要有值班人；「商业化生产 = 自动收费」则必须 **P0 重做支付链路**。

### ✅ 已修复（2026-08-27）：人工收款闭环上线

按「先做人工闭环」落地，把「客服手动开权限」做成**可运营流程**，收钱到开通不再靠口头喊人：

1. **用户端**：`POST /billing/upgrade`（[billing.py](../backend/app/routers/billing.py)）→ 申请落库 `plan_upgrade_requests`，返回订单号（`VS{日期}{随机}`）+ 金额 + 转账说明；重复提交同套餐待处理申请自动去重；账单页（[BillingPage.tsx](../frontend/src/pages/billing/BillingPage.tsx)）展示「我的升级申请」状态（待确认/已开通/已拒绝）。
2. **管理员端**：邮箱在 `ADMIN_EMAILS`（默认 `admin@veyaship.com`）→ `GET /billing/admin/upgrades` 待办+历史对账（按状态筛选），一键 `approve`（改 plan + 积分加满）或 `reject`（留原因）；`/auth/me` 返回 `is_admin` 供前端显隐「升级审核」入口（[AdminUpgradesPage.tsx](../frontend/src/pages/billing/AdminUpgradesPage.tsx)）。权限在 `require_admin` 依赖强制，前端隐藏只是 UX。
3. **防呆**：审批仅允许 `pending`（重复操作 400）；`handled_by/handled_at/note` 全记录，可追溯。
4. **测试**：`tests/test_billing_manual.py` 8 用例（落库/去重/403/审批改套餐/拒绝/重复 400）全过 + 真实服务器冒烟 13 项全过。

> 刻意不做：自动收款（支付宝/微信支付回调、Creem 验签）。人工闭环已验证可运营，接入自动支付时只需在 `approve` 处换成回调触发即可，业务模型（申请表状态机）不用动。

### 2. 安全基线：三个真漏洞

| 漏洞 | 位置 | 说明 | 修复方向 |
|------|------|------|----------|
| **SSRF 内网可达** | [crawler/scraper.py:30](backend/app/services/crawler/scraper.py#L30) `fetch_page` | 用户传任意 URL 直接 `httpx.get`；[L60](backend/app/services/crawler/scraper.py#L60) `urlparse` 只存域名不校验 → `169.254.169.254`（云元数据）、内网端口可达。Agent「帮我抓这个链接」是入口 | URL 白名单（仅允许 1688/Shopify 等已知域名）+ 拒绝私网/环回地址 |
| **API Key 明文存储 + 明文回显** | [settings.py:88](backend/app/routers/settings.py#L88) 写 `SystemConfig`；[L77-78](backend/app/routers/settings.py#L77) GET 返回全文 | 服务商 key（Onebound）明文落库；DB 泄漏 = 平台统一配置的 key 全暴露；管理端回显明文 | 加密存储 + 回显掩码（`sk-****ab12`） |
| **JWT 密钥空值不拒启** | [config.py:79](backend/app/core/config.py#L79) `JWT_SECRET_KEY=""`；[main.py:70](backend/app/main.py#L70) 只 WARNING | 空密钥 = HMAC 空串签名 = **任意 token 可伪造** | 启动时密钥缺失即抛异常拒绝启动 |

另：CORS（[main.py:149](backend/app/main.py#L149)）默认 localhost 白名单 + `allow_credentials=True`，本身安全；但生产域名必须显式配进 `BACKEND_CORS_ORIGINS`，**禁止配 `*` + credentials**。

### 3. 无备份机制：数据丢失不可逆

- 单机 ECS 跑 PG，repo 内未发现任何备份任务 / 策略 / cron
- 数据丢失 = 业务死亡，属于运营命门
- 待确认：服务器层是否有外部 cron 备份；若没有，**上线前必须有**（每日自动 dump + 异地保留）

---

## P1 —— 上线前应修

### 4. 任务队列 + 幂等

- `POST /agent/run`（[agent.py:121](backend/app/routers/agent.py#L121)）**同步跑完整个 ReAct 循环**（实测 30~90s），HTTP 一直挂着，前端只能转圈；并发 10 用户 = 10 worker 占满 90s
- 内容生成（[content.py:260](backend/app/routers/content.py#L260)、[images.py:121](backend/app/routers/images.py#L121)）是 `asyncio.create_task` **fire-and-forget** —— 无任务表、无状态、无重试，进程重启任务丢失
- [scheduler.py:158](backend/app/services/scheduler.py#L158) 自认「would be replaced by a proper task queue (Celery/RQ)」
- **无幂等键**：客户端超时重试 = 同一指令扣两次积分、建两个对话

修复方向：任务表 + 状态机 + 前端轮询；任务自带 idempotency key。

### 5. 可观测性（最小集）

- [main.py:22](backend/app/main.py#L22) 单一 logger → stdout；RequestLogMiddleware 记 `方法 路径 → 状态码 耗时`
- 缺失：request ID / 链路 ID（Agent 多步出错无法串联）、结构化日志、指标面板、告警
- 最小可落地：Sentry 错误告警 + 请求/Agent 步链路 ID + 结构化 JSON 日志

### 6. 限流换 Redis + 修 500

- 限流**已存在**（[rate_limit.py](backend/app/core/rate_limit.py)），挂在 agent / analytics / auth 上；但：
  - **纯内存存储**（[L26](backend/app/core/rate_limit.py#L26)）→ 多 worker 各自计数，限流变 N 倍失效
  - **按 IP 不按用户**（[L91](backend/app/core/rate_limit.py#L91)）→ 同公司 IP 共享会被连带 429，换 IP 可绕过
- 积分扣减本身是好的：`deduct_credits`（[user.py:72](backend/app/models/user.py#L72)）`with_for_update()` 行级锁 + 保存点，防并发扣超 ✅
- **附加 bug**：[agent.py:179](backend/app/routers/agent.py#L179) 扣积分抛 `ValueError` 未捕获 → 并发抢最后一分时返回 500 而非 402；应 `except ValueError → HTTPException(402, "积分不足")`

### 7. 迁移部署流程确认

- Alembic 迁移目录在（`backend/migrations/`），但 cicd-deploy.sh 部署时是否自动跑 `alembic upgrade head` **未验证**
- schema 与代码漂移在商业化上是事故级，需确认或补上

---

## P2 —— 可后置（扩实例或体验优化时再做）

### 8. 分布式定时任务

- [scheduler.py:23](backend/app/services/scheduler.py#L23) `AsyncIOScheduler` 跑在进程内，**单实例假设**
- 当前单机部署不出事；多 worker / 多容器会：`_run_store_checks` 每实例跑一遍 → StoreCheckLog 重复行；`_expire_subscriptions` 有 `is_active==True` 过滤基本幂等
- 修复：PG advisory lock 包住各 job（在加第二台实例**之前**做掉）

### 9. 流式输出

- 后端 grep `StreamingResponse | SSE | WebSocket` **零命中**；DeepSeek 调用本身非流式（`llm.generate`）；前端 `isPending` 转圈
- 纯体验优化，不阻塞收款；异步任务 + 轮询落地后再用 SSE 推流

### 10. 前端健壮性

- 全站无 `ErrorBoundary`；LLM 驱动 UI（已踩过 `risks.map is not a function`）运行时 throw = 白屏
- 加一个顶层 ErrorBoundary 是几十行的小成本保险

### 11. 其他

- JWT 7 天无撤销（`ACCESS_TOKEN_EXPIRE_MINUTES=10080`）；可接受，加 refresh + 登出后置
- i18n：目标用户为中文跨境卖家，中文 UI 是正确取舍，非 gap

---

## 业务依赖风险（非代码 bug，但影响可能最大）

| 风险 | 说明 | 应对 |
|------|------|------|
| **1688 反爬封 IP** | 核心功能 F2 依赖抓取 1688，数据中心 IP 被封是常态，封了 F2 就瘫 | 代理池 / 降级通道 / 应急预案，属业务生死线 |
| **LLM 供应商稳定性** | DeepSeek/Replicate 已有 tenacity 重试 + 超时（[deepseek.py:75](backend/app/services/ai/deepseek.py#L75)、[replicate.py:48](backend/app/services/ai/replicate.py#L48)）✅；但未见熔断 + 降级自动化 | 确认通义万相 → FLUX 降级是代码自动触发还是手动 |

---

## 修复优先级总表

| 等级 | 项 | 一句话 | 成本 |
|------|----|--------|------|
| P0 | 支付闭环 | ✅ 人工闭环已上线（申请→转账→审核开通→对账）；**自动收款（Creem 验签）后置** | 中大 |
| P0 | 安全基线（SSRF / API Key / JWT） | ✅ 已修：IP 校验 / Fernet 加密+掩码 / 空密钥拒启 | 小 |
| P0 | 无备份 | ✅ 已修：deploy/backup.sh 定时备份 | 小 |
| P1 | 任务队列 + 幂等 | ✅ 已修：异步状态机 + Idempotency-Key + 僵尸恢复 | 中大 |
| P1 | 可观测性最小集 | ✅ 已修：Sentry 告警 + 链路 ID | 小 |
| P1 | 限流 + 修 500 | ✅ 已修：数据库窗口计数；**Redis 化可后置** | 小 |
| P1 | 迁移部署流程确认 | ✅ 已修：Alembic + 启动 create_all + deploy 脚本 | 小 |
| P2 | 分布式定时 | ✅ 已修：PG advisory lock 防重 | 小 |
| P2 | 流式输出 | ⏳ 待做：纯体验优化，需 SSE 基建 | 中 |
| P2 | ErrorBoundary | ✅ 已修：顶层兜底防白屏 | 小 |

---

## 附：代码证据索引

| 主题 | 位置 |
|------|------|
| 支付人工闭环（已修） | [billing.py](backend/app/routers/billing.py)、[plan_upgrade.py](backend/app/models/plan_upgrade.py)、[006 迁移](backend/migrations/versions/006_add_plan_upgrades.py) |
| 支付死代码 / webhook 空壳（后置） | [payments.py:163](backend/app/api/v1/endpoints/payments.py#L163)、[payment.py:75](backend/app/services/payment.py#L75) |
| SSRF | [crawler/scraper.py:30](backend/app/services/crawler/scraper.py#L30)、[L60](backend/app/services/crawler/scraper.py#L60) |
| API Key 明文 | [settings.py:88](backend/app/routers/settings.py#L88)、[L77](backend/app/routers/settings.py#L77) |
| JWT 空密钥 | [config.py:79](backend/app/core/config.py#L79)、[main.py:70](backend/app/main.py#L70) |
| CORS | [main.py:149](backend/app/main.py#L149)、[config.py:84](backend/app/core/config.py#L84) |
| 积分行级锁 | [user.py:72](backend/app/models/user.py#L72) |
| 限流内存实现 | [rate_limit.py:26](backend/app/core/rate_limit.py#L26)、[L91](backend/app/core/rate_limit.py#L91) |
| agent 同步执行 | [agent.py:121](backend/app/routers/agent.py#L121) |
| 扣分 500 泄漏 | [agent.py:179](backend/app/routers/agent.py#L179) |
| fire-and-forget | [content.py:260](backend/app/routers/content.py#L260)、[images.py:121](backend/app/routers/images.py#L121) |
| APScheduler 单实例 | [scheduler.py:23](backend/app/services/scheduler.py#L23) |
| 日志 stdout | [main.py:22](backend/app/main.py#L22) |
| LLM 重试 | [deepseek.py:75](backend/app/services/ai/deepseek.py#L75)、[replicate.py:48](backend/app/services/ai/replicate.py#L48) |
