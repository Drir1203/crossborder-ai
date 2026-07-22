---
description: 展示当前项目代码框架、功能清单，并与上一版本对比新增/变更的代码
---

# 项目代码框架对比

当用户输入 `/project-summary` 或要求你展示项目框架和变更时，按以下步骤执行：

## 步骤 1：展示代码框架

从项目根目录（`D:\Project\crossborder-ai`）展示核心目录结构，**排除** `node_modules`、`__pycache__`、`.git`、`venv`、`dist`、`.vite` 等无关目录。

```bash
cd /d/Project/crossborder-ai
# 后端结构（只展示 app/ 下的 py 文件）
find backend/app -name '*.py' | sort
# 前端结构（只展示 src/ 下的 ts/tsx 文件）
find frontend/src -name '*.ts' -o -name '*.tsx' | sort
```

## 步骤 2：git 变更对比

用 git 对比当前代码与上一个版本的差异（默认对比上一次 commit）：

```bash
cd /d/Project/crossborder-ai
# 显示新增/变更的文件列表（按目录分组）
git diff HEAD~1 --stat
# 显示新增文件列表（untracked）
git status --short
```

如果用户想对比其他版本（比如对比某个 tag、分支、或指定 commit），让用户指定。

## 步骤 3：汇总输出格式

按以下模版输出：

---

## 📁 项目代码框架

### 后端 (backend/app/)
```
（目录树输出）
```

### 前端 (frontend/src/)
```
（目录树输出）
```

## 🧩 功能模块

| 模块 | 路由 | 状态 |
|------|------|------|
| F1 Dashboard | /dashboard | ✅ |
| ... | ... | ... |

（参考 CLAUDE.md 中的功能模块清单）

## 📊 本次变更

### 新增文件
- `path/to/file` — 说明

### 修改文件
- `path/to/file` — 说明

### 删除文件
- 无

---

## 步骤 4：展示关键代码片段

对新增或大幅修改的文件，展示其核心函数/组件签名，帮助用户快速了解变更内容。

每个文件展示不超过 10 行关键代码（函数签名、class 定义、路由定义），用注释说明作用。
