# CAP-01 · 1688 抓取健壮性与平台级 Key 就绪体验

> 状态：已确认实施 · 日期：2026-09-03
> 归属模块：F2 Refinery（`/products/scrape`）+ 共享服务 `backend/app/services/scraper.py`

## 1. 背景与问题

面向**非技术跨境卖家**，1688 抓取是他们把货拉进系统的入口。诊断结论：

- 平台（VeyaShip）未配置 Onebound 数据服务 Key 时，抓取会走"直接抓 1688 HTML"的笨路径：慢、易被反爬、甚至裸抛英文/异常给前端 → 卖家看到 500 / 看不懂的错误。
- 抓取失败没有稳定错误码与中文可读信息，卖家无法判断"换链接 / 重试 / 手动录入 / 联系客服"。
- 商品字段缺失时整单失败；价格/标题等解析异常没有兜底。

## 2. 能力点

| # | 能力点 | 关键产出 |
|---|--------|---------|
| C1 | **平台级 Key 就绪提示**：抓取前检查平台数据服务是否就绪，未就绪给中文引导，不甩 5xx/英文 | 路由开头就绪检查 + `GET /products/scrape/status` |
| C2 | **错误分类映射**：链接无效/已下架/解析失败/被风控/超时 → 稳定错误码 + 中文 message | scraper 异常层次 `ScrapeError` 族 + 路由统一转 `HTTPException` |
| C3 | **降级直抓链路**：Onebound → 失败自动降级直抓 → 返回标注 `data_source` | `data_source: onebound / direct` |
| C4 | **商品数据清洗**：字段兜底 + 明显异常归类 | 标题空 / 价格 0 → `parse_error`；价格缺失 → `None` 不整单失败 |
| C5 | **前端就绪/错误体验**：按钮禁用+hint、按错误码给建议 | ProductsPage |

## 3. 需求场景

**R1（就绪）**
- Given 平台未配置 Onebound key（SystemConfig 与 settings 均空）
- When 卖家 POST `/products/scrape`
- Then 返回 400，`detail={code:"service_not_configured", message:"数据抓取服务暂未开通，请联系平台客服开通后再试"}`，不发网络请求
- And 前端 `GET /products/scrape/status` 返回 `configured:false`，抓取按钮禁用并提示

**R2（链接无效）**
- Given 平台已配置 Key，URL 非 1688 商品链接 / 无 offer ID
- Then 返回 400，`code:"invalid_url"`，中文说明

**R3（已下架/不存在）**
- Given 数据源（Onebound 或直抓页）明确提示商品不存在/下架
- Then 返回 404，`code:"product_not_found"`，引导换链接

**R4（降级直抓成功）**
- Given Onebound 暂时失败（超时/服务异常/返回空），直抓 HTML 能解析出标题
- Then 抓取成功 201，`data_source:"direct"`，字段清洗后落库

**R5（直抓也失败 / 全链路失败）**
- Given Onebound 与直抓都失败
- Then 返回 4xx 分类错误（优先保留数据服务的分类），**绝不低于 500**，不裸抛异常

**R6（字段兜底与清洗）**
- Given 直抓/接口拿到标题但缺价格、销量、店铺
- Then 落库成功，缺失字段为 `None`，不整单失败
- Given 解析到价格 ≤ 0 或标题为空
- Then 归类 `parse_error`（400，中文提示换链接或手动录入）

## 4. 稳定错误码表（detail 结构 `{code, message}`）

| code | HTTP | message（卖家可读，中文） | root cause / 给卖家的下一步 |
|------|------|--------------------------|------------------------------|
| `service_not_configured` | 400 | 数据抓取服务暂未开通，请联系平台客服开通后再试 | 平台无 Onebound key；客服介入 |
| `invalid_url` | 400 | 链接无效：仅支持 1688.com 商品详情链接 | 不是 1688 / 无 offer ID / SSRF 输入；换链接 |
| `product_not_found` | 404 | 该商品不存在或已下架，请换一个 1688 商品链接试试 | 下架/删除/接口明确无此商品；换链接 |
| `parse_error` | 400 | 商品信息解析异常（标题或价格缺失/为 0），请换链接或手动录入 | 页面结构变化/反爬伪装/异常值；重试或手动录入 |
| `anti_bot` | 400 | 1688 有访问保护，暂时无法自动抓取，请稍后重试或手动录入 | 直抓被风控（验证码/x5sec/短页面） |
| `timeout` | 400 | 抓取超时，请稍后重试 | Onebound/直抓站点响应超时 |
| `service_unavailable` | 400 | 数据服务暂时不可用，请稍后再试 | Onebound 服务端错误/Key 无效/降级也失败 |

> 说明：错误面全部 4xx（卖家可见）——业务错误不打 5xx；服务端日志保留原始异常用于运维定位。

## 5. 降级与数据源标注策略

```
POST /products/scrape
 └ 就绪检查（DB SystemConfig > settings 兜底）无 Key → service_not_configured (400)
 └ scrape_1688(url, key, secret)
    ├ URL 校验 + offer ID → invalid_url
    ├ 有 Key → _fetch_onebound（code=0 成功；明确不存在 → product_not_found 直接抛；
    │          超时/服务异常 → 记为一次暂时性失败）
    │     成功 → 清洗落库，data_source="onebound"
    ├ 无 Key 或 Onebound 暂时失败 → _direct_fetch（httpx → curl_cffi 模拟 Chrome）
    │     成功 → 清洗落库，data_source="direct"
    ├ 直抓明确下架 → product_not_found；被拦 → anti_bot；超时 → timeout
    ├ 仍失败 → 有 Onebound 暂时性失败则抛其分类，否则抛直抓分类
    └ 成功统一 _normalize_product 清洗（标题必填；价格显式但 ≤0 → parse_error；缺失字段 → None）
```

`data_source` 随成功响应返回（onebound / direct），供统计与前端提示"数据源：实时抓取"。

## 6. 兼容约束

- `ScrapeError` 继承 `RuntimeError`（旧 `except RuntimeError` 仍兼容）；
- `InvalidUrlError` 同时继承 `ValueError` + `ScrapeError`（既有 `test_scrape_1688_rejects_non_1688_url` 期望 `ValueError` 不破）；
- 成功返回仍含 `url/title/main_image_url/price/sales_count/shop_name`（radar / agent 直接调用不破）。

## 7. 验收测试（backend/tests/test_products_scrape.py）

Key 未配置→400 中文；status 端点 false→true；无效 URL→invalid_url；下架→404；
Onebound 失败→直抓成功 data_source=direct；全失败→4xx 不 500；价格缺失兜底 None；
价格 0→parse_error。`python -m pytest tests/test_products_scrape.py -q` 全绿，
且 `tests/test_products.py`、`tests/test_security_fixes.py` 不回归。
