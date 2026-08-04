# 项目文档导航 📚

> 所有 md 文档一览：作用 + 什么时候看
> 更新时间：2026-08-04

> **新手建议阅读顺序**：`README`（是什么）→ `CLAUDE.md`（怎么开发）→ `AGENT_ROADMAP.md`（核心功能）→ `DEPLOYMENT.md`（怎么部署）

---

## 一、项目基础与约定

| 文件 | 作用 | 什么时候看 |
|------|------|-----------|
| **CLAUDE.md** | 项目约定：技术栈、目录结构、后端/前端编码规范、F1-F9 功能模块清单、关键规则 | ⭐ 开发必读 |
| **CONTEXT.md** | 项目背景快照：用户画像（跨境卖家，不懂技术）与产品定位 | 了解产品面向谁 |
| **README.md** | 项目门面介绍（英文）：AI 选品决策引擎定位 | 对外展示 |

## 二、Agent / AI 核心功能

| 文件 | 作用 | 什么时候看 |
|------|------|-----------|
| **AGENT_ROADMAP.md** | ⭐ Agent 架构 + 路线图：ReAct/Function Calling、9 个工具、6 个工作流、选品/单品/合规/巡检闭环、4.2 自我反思、5.0 定时 Agent 进度 | 了解 Agent 全貌与下一步规划 |
| **AGENT_TESTING.md** | Agent 测试指南：前提条件、6 类测试用例、**闭环 vs 指令化验证方法**、检查清单 | 测试/验收 Agent 功能 |
| **AI_WORKFLOW_PLAN.md** | AI 工作流优化方向（6 个方向，早期规划） | 看历史规划（部分已实现） |

## 三、部署

| 文件 | 作用 | 什么时候看 |
|------|------|-----------|
| **DEPLOYMENT.md** | ⭐ 部署架构 + GitHub Actions CI/CD 流水线 + 技术决策 + 回滚方案（面试可讲） | 部署/运维/面试 |
| **DEPLOYMENT_CHECKLIST.md** | 从零部署的操作清单（早期，偏一次性引导） | 重新从零部署时 |
| **DEPLOYMENT_COMPLETE.md** | 上线备忘：访问地址、ICP 备案待办、后续事项 | 看线上状态与待办 |

## 四、商业 / 战略 / 面试

| 文件 | 作用 | 什么时候看 |
|------|------|-----------|
| **COMMERCIALIZATION_PLAN.md** | 商业化方案：从验证项目到市场产品的路径 | 思考商业模式 |
| **FUNDABLE_DIRECTIONS.md** | 可融资方向分析（投资人视角） | 融资/转型评估 |
| **FUTURE_ASSESSMENT.md** | 竞争力与未来发展诚实评估 | 战略反思 |
| **POSITIONING_COMPARISON.md** | 定位对比：Listing 生成器 vs AI 决策引擎 | 讲故事/定位 |
| **COMPETITOR_ANALYSIS.md** | 竞品分析（GitHub 开源项目） | 竞品调研 |
| **COMPETITOR_LANDSCAPE.md** | 竞品格局（店小秘/店匠/领星等平台） | 竞品调研 |
| **UX_PRICING_REVIEW.md** | 功能菜单 & 定价策略分析 | 调整产品/定价 |
| **INTERVIEW_GUIDE.md** | 面试话术：Agent 技术 + 商业化应答框架 | ⭐ 面试前 |
| **RESUME.md** | 简历内容（AI 全栈岗）：标题字数安全版、主版本、精简版、面试准备表 | ⭐ 投简历前 |

## 五、功能规划 / 审查

| 文件 | 作用 | 什么时候看 |
|------|------|-----------|
| **MINIPROGRAM_PLAN.md** | 微信小程序开发计划 | 小程序相关工作 |
| **QA_REVIEW.md** | QA 审查报告（前端 UI、后端 API、体验问题） | 看已知问题清单 |

---

## 使用提示

- **已经过时/偏历史**的文档：`AI_WORKFLOW_PLAN.md`、`DEPLOYMENT_CHECKLIST.md`（早期规划，部分已落地）
- **当前最核心**的文档：`CLAUDE.md`（开发）、`AGENT_ROADMAP.md`（功能）、`DEPLOYMENT.md`（部署）、`INTERVIEW_GUIDE.md`（面试）
- **代码为最终依据**：文档描述能力，实际以 `backend/app`、`frontend/src` 代码为准
