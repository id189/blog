# ⚡ 霓光志 · 个人 AI 技术博客

一个 **浅色明快 + 霓虹科技感** 风格的纯静态技术博客，基于 [Astro](https://astro.build) 构建。
文章用 Markdown 写，推送到 GitHub 即自动构建发布。

## ✨ 特性

- 🎨 浅色霓虹科技风：玻璃拟态卡片 + 浮动光球 + 渐变文字
- 📝 内容即 Markdown：在 `src/content/posts/` 丢一个 `.md` 就自动生成列表/详情
- 📑 文章详情页带自动目录（TOC）与滚动高亮
- 🔍 首页右侧栏：**全文搜索**（Pagefind 索引文章正文）+ **分类筛选**，可与搜索叠加
- 🚀 推送 GitHub 即自动部署（Netlify / Cloudflare Pages / Vercel）
- 📱 完整响应式：桌面 / 平板 / 手机都好看

## 🗂 目录结构

```
blog/
├─ src/
│  ├─ content/posts/*.md     ← 你的文章放这里
│  ├─ components/            ← 组件（Header/Footer/Hero/PostCard/GlowOrb/Toc）
│  ├─ layouts/Base.astro     ← 全局壳 + 字体
│  ├─ pages/                 ← 页面（首页/文章/关于/404）
│  ├─ styles/global.css      ← 设计系统 token（改配色改这里）
│  └─ consts.ts              ← 站名/作者/导航（改文案改这里）
├─ public/favicon.svg
├─ astro.config.mjs
└─ netlify.toml
```

## ✍️ 新增 / 更新一篇文章

本站用 **Astro Content Collections** 管理文章：所有 `.md` 都放在 `src/content/posts/`，
**新增或编辑任意 `.md`，构建时即自动生成首页列表与 `/posts/<slug>` 详情页，无需手动登记。**

1. 在 `src/content/posts/` 新建 `我的文章.md`，头部写上 frontmatter：

   ```md
   ---
   title: "文章标题"          # 必填
   description: "一句话简介，显示在卡片与 SEO"   # 必填
   date: 2026-07-12          # 必填
   tags: ["大模型", "教程"]   # 可选
   category: "AI 应用"        # 可选，首页右侧栏按此筛选
   emoji: "🚀"               # 可选，卡片封面占位图
   cover: ""                 # 可选，封面图路径（放 public/ 下）
   author: "你的名字"         # 可选
   draft: false              # 可选，true 则不发布
   ---

   正文用 Markdown 写，支持代码块、引用、表格……
   ```

   > 必填字段为 `title` / `description` / `date`；三者齐全即可被收录。
   > 想临时隐藏某篇，把 `draft` 设为 `true` 即可，它不会出现在列表与详情页。

2. 本地预览：`npm run dev`，打开 http://localhost:4321 看效果。
3. 提交并推送（**编辑已有 `.md` 同样会自动更新**）：

   ```bash
   git add .
   git commit -m "新增：我的文章"
   git push
   ```

托管平台检测到 push 后会自动构建并发布。✅

## 🔧 本地开发

```bash
npm install      # 首次安装依赖
npm run dev      # 本地预览（带热更新）
npm run build    # 构建到 dist/
npm run preview  # 预览构建结果
```

## 🚀 部署（基于 GitHub 仓库同步）

文章通过 GitHub 仓库同步：写好 `.md` → `git push` 到 `main` → 平台自动构建 `dist/` 并发布。

仓库已为三家平台备好兼容配置：

| 平台 | 配置文件 | 构建命令 | 输出目录 |
| --- | --- | --- | --- |
| **Netlify** | `netlify.toml` | `npm run build` | `dist` |
| **Vercel** | `vercel.json` | `npm run build` | `dist` |
| **Cloudflare Pages** | 无需文件 | `npm run build` | `dist` |
| **GitHub Pages** | `.github/workflows/deploy.yml` | `npm run build` | `dist`（经 Pages Artifact） |

### 方式 A：Netlify（默认，已附 `netlify.toml`）
1. 登录 Netlify → “Add new site” → 关联 GitHub 仓库 `blog`。
2. 构建命令 `npm run build`、发布目录 `dist`（已写在 `netlify.toml`，自动识别）。
3. 之后每次 `git push` 到 `main` 自动部署。

### 方式 B：Cloudflare Pages
关联仓库 `blog`，构建命令 `npm run build`，输出目录 `dist`，框架预设选 Astro（无需配置文件）。

### 方式 C：Vercel
关联仓库 `blog`，框架预设选 Astro（构建 `npm run build`、输出 `dist`，已写在 `vercel.json`，自动识别）。

### 方式 D：GitHub Pages（无需第三方账号，仓库自带工作流）
访问地址：`https://id189.github.io/blog/`（项目站点，路径前缀 `/blog/`）。

1. 仓库已内置 `.github/workflows/deploy.yml`：推送 `main` 即自动构建并发布到 GitHub Pages。
2. 首次需手动开启一次：仓库 **Settings → Pages → Build and deployment → Source 选 “GitHub Actions”**。
3. 之后每次 `git push` 到 `main` 自动部署；在仓库 **Actions** 标签页可看进度，部署完成后站点即更新。
4. 工作流通过环境变量 `ASTRO_BASE=/blog/`、`ASTRO_SITE=https://id189.github.io` 注入子路径，
   站内链接、资源、Pagefind 搜索索引均自动适配该路径。

> 想改 GitHub 用户名或仓库名时，把工作流里的 `ASTRO_SITE` 与 `ASTRO_BASE` 同步改成对应值即可。

### 设置站点域名（可选）
仓库已在 `astro.config.mjs` 预留 `site` 字段（占位 `https://example.netlify.app`）。
连接平台后，在平台的**环境变量**里设置 `ASTRO_SITE` 为你的真实域名（如 `https://blog.example.com`），
构建时会自动覆盖，用于生成规范链接与 sitemap。GitHub Pages 方式已在工作流中固定 `ASTRO_SITE`/`ASTRO_BASE`，
无需在平台侧额外设置。

> 所有方式都不需要任何 Token；内容同步始终基于 GitHub 仓库 `blog`。
> 内容同步仍基于 GitHub 仓库。

## 🎨 改文案 / 配色

- **站名 / 作者 / 导航 / 社交**：编辑 `src/consts.ts`。
- **配色与视觉**：编辑 `src/styles/global.css` 顶部的 `:root` 变量（蓝/紫/青/品红在此）。

---

Made with ♥ & neon glow · Powered by Astro
