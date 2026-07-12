---
title: "用 Astro 搭建你的第一个静态博客"
description: "从零开始，用 Astro + Markdown 搭一个轻量、快速、可自动部署的个人博客。"
date: 2026-07-12
tags: ["Astro", "教程", "前端"]
category: "技术笔记"
emoji: "🚀"
author: "你的名字"
draft: false
---

静态博客的魅力在于：**内容即数据，构建即发布**。这篇笔记带你用 [Astro](https://astro.build) 从零搭一个能自动部署的博客。

## 为什么选 Astro

Astro 默认输出纯静态 HTML，几乎不带运行时 JS，因此加载极快。它原生支持：

- Markdown / MDX 写作
- 内容集合（Content Collections）做类型校验
- 任意部署平台（GitHub Pages、Netlify、Vercel、Cloudflare Pages）

> 一句话：**写 Markdown，推到仓库，网站就更新了。**

## 项目结构

一个最小博客通常长这样：

```text
src/
├─ content/posts/     # 你的文章（.md）
├─ components/        # 组件
├─ layouts/           # 页面外壳
├─ pages/             # 路由
└─ styles/global.css  # 设计系统
```

## 写第一篇文章

在 `src/content/posts/` 下新建一个 `.md`，头部写上 frontmatter：

```md
---
title: "文章标题"
description: "一句话简介"
date: 2026-07-12
tags: ["AI", "教程"]
emoji: "🚀"
---

正文用 Markdown 写……
```

## 本地预览

```bash
npm install
npm run dev      # 本地预览（带热更新）
npm run build    # 构建到 dist/
```

<div class="callout">
  <span class="ico">💡</span>
  <span>构建产物在 <code>dist/</code> 目录，是一个纯静态站点，丢到任何静态托管都能跑。</span>
</div>

## 下一步

- 配置自动部署（下一篇讲）
- 加上标签、分类、搜索
- 做一套自己的视觉主题

写博客最难的从来不是技术，而是**开始写**。现在就新建一个 `.md` 试试吧。
