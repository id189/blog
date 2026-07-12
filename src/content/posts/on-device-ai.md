---
title: "前端也能玩转 AI：浏览器里的本地推理"
description: "不用服务器，用 WebGPU 和 Transformers.js 在浏览器里直接跑大模型。"
date: 2026-07-08
tags: ["前端", "WebGPU", "AI"]
category: "前端 AI"
emoji: "⚡"
author: "你的名字"
draft: false
---

很多人以为跑大模型必须有一台 GPU 服务器。其实，**现代浏览器已经能本地推理了**。

## 为什么是浏览器

- 隐私：数据不出本机
- 零成本：不需要后端算力
- 低延迟：模型加载后随用随走

## Transformers.js 上手

[Transformers.js](https://github.com/huggingface/transformers.js) 让我们可以在浏览器里加载 Hugging Face 模型：

```js
import { pipeline } from "@huggingface/transformers";

const classifier = await pipeline(
  "sentiment-analysis",
  "Xenova/distilbert-base-uncased-finetuned-sst-2-english"
);

const result = await classifier("I love building AI blogs!");
console.log(result); // [{ label: "POSITIVE", score: 0.99 }]
```

## WebGPU 加速

新版浏览器支持 WebGPU，推理速度比纯 CPU 快一个数量级：

```js
const generator = await pipeline("text-generation", "model-id", {
  device: "webgpu",
});
```

> 注意：首次加载模型需要下载权重（几十到几百 MB），适合「加载一次、频繁使用」的场景。

## 适合做什么

- 文本分类、情感分析
- 翻译、摘要
- 轻量对话 / 补全

不适合：超大参数模型、超高并发服务。

把 AI 搬进浏览器，是前端的全新玩法。你的下一个 side project，也许就该在 `<canvas>` 旁边加一个 `<model>` 了。
