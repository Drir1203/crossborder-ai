# CAP-07 新手激活引导 + 空状态导流 + 图结果历史展示（前端激活与留存）

> 前端 React18 + TS。目标用户：非技术跨境卖家。全部文案中文。
> 规则：引导要「点几下就能跑通第一个闭环」，不堆功能说明；不强制阻断（可关/可跳过）。

## 能力点

- **C1 三步激活引导卡**：Dashboard 空状态主区块，向新用户暴露「绑定店铺 → 设品牌调性 → 出第一张 AI 图」的最小闭环。
- **C2 空状态导流**：图片历史为空 / 图片生成端点暂不可用时，给出引导文案与到目标页的跳转。
- **C3 图结果历史画廊**：Dashboard 展示本人最近生成的图（缩略图 + prompt 前 N 字 + 模型徽标 + 相对时间），点击放大预览。
- **C4 完成勾选**：三步各自用真实后端信号勾「已完成」，不靠占位假数据。
- **C5 不再打扰**：绑定过店铺 / 已生成过图 / 用户跳过三者满足其一即永久隐藏引导。

## 需求场景

1. 新注册卖家首次进 Dashboard：看到引导卡（非 modal、可滚可关），按①→②→③点几下即可跑到「生成第一张图」，不要求先读懂整套后台。
2. 老卖家 / 已绑定店铺 / 已有成图的用户：不再看到引导，不打扰。
3. 卖家进 Dashboard：最近生成的图在首屏下方一目了然，能点开看大图、看到用的模型与生成时间。
4. 卖家点了引导「去绑定」→ 绑定后回到 Dashboard：引导自动消失（信号命中），不再重复问。

## 触发 / 完成判定（本地信号）

| 项 | 前端本地信号来源 | 判定 |
| --- | --- | --- |
| 引导是否显示 | localStorage 标记 `veyaship_onboarded_seen` | 无标记才可能显示 |
| 停止打扰（隐藏引导） | 任一命中即隐藏：标记存在 / `GET /shopify/channels` 非空 / `GET /images/history` 存在 `status==='completed'` | 满足其一 |
| 步骤①店铺已绑 | `GET /shopify/channels` | 返回数组长度 > 0 |
| 步骤②调性已设 | `GET /settings/persona` | 返回对象含 `brand_name / tagline / description / banned_words(非空)` 任一非空 |
| 步骤③素材已跑 | `GET /images/history` | 存在 `status==='completed' && image_urls.length>0` |
| 图片画廊可见 | `GET /images/history` | 端点可用；只展示 completed，最多 6 张 |
| 端点暂不可用 | 上述查询抛错 / 404 | 静默降级：相关勾选保持未完成、画廊整块隐藏，页面不崩 |

## 端点契约（只读，不改后端）

- `GET {API}/shopify/channels` → `Array<{id, shop_name, domain, created_at}>`（未绑定为空数组）
- `GET {API}/settings/persona` → `{brand_name?, tagline?, description?, tone?, tone_custom?, banned_words[]}`（无记录返回默认值，200）
- `GET {API}/images/history` → `{items: [{id, prompt, status, image_urls[], model_used?, error?, created_at?}]}`（仅本人数据、时间倒序；CAP-07 并行代理实现中，未接通前端按 404 降级处理）

## 跳转目标路由（均已确认存在于 `frontend/src/App.tsx`）

- ① 绑定 Shopify 店铺 → `/app/shopify`
- ② 设置品牌调性 → `/app/settings`（SettingsPage 默认激活 tab 即 persona）
- ③ 生成第一张 AI 图 → `/app/images`
- 画廊空态「去生成第一张图」 → `/app/images`

## 涉及文件

- 新增 `frontend/src/components/dashboard/useOnboarding.ts`：契约类型 + 本地标记 + 三个信号 useQuery（`retry:false`、失败静默）+ 相对时间工具。
- 新增 `frontend/src/components/dashboard/OnboardingGuide.tsx`：三步激活引导卡（可跳过）。
- 新增 `frontend/src/components/dashboard/ImageHistoryGallery.tsx`：图结果历史画廊 + 放大预览（轻量自实现 modal，未引新依赖）。
- 修改 `frontend/src/pages/dashboard/DashboardPage.tsx`：挂载以上两个区块（引导在头部问候下方、画廊在「最近操作」上方）。

不新增第三方依赖；不触碰 pages/shopify、pages/content、pages/settings、backend。
