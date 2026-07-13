---
title: "大模型应用入门：从 API 到 RAG"
description: "搞懂大模型应用的三层结构—— Prompt、函数调用、检索增强生成（RAG）。"
date: 2026-07-10
tags: ["大模型", "RAG", "AI"]
category: "AI应用"
emoji: "🧠"
author: "你的名字"
draft: false
---

和大模型打交道，本质是在**管理上下文**。这篇笔记梳理从最简单的 API 调用，到检索增强生成（RAG）的演进。

## 第一层：Prompt

最基础的用法，就是把问题拼进提示词发给模型：

```python
from openai import OpenAI

client = OpenAI()
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "你是一个友善的助手。"},
        {"role": "user", "content": "用一句话解释什么是向量数据库？"},
    ],
)
print(resp.choices[0].message.content)
```

## 第二层：函数调用（Tool Use）

让模型「决定」要不要调用你的函数，比如查天气、查数据库：

```json
{
  "name": "get_weather",
  "description": "查询某城市天气",
  "parameters": {
    "type": "object",
    "properties": { "city": { "type": "string" } }
  }
}
```

## 第三层：RAG（检索增强生成）

当知识不在模型脑子里时，先**检索**再**生成**：

1. 把文档切片并转成向量存入向量库
2. 用户提问时，检索最相关的片段
3. 把片段拼进 Prompt，交给模型生成答案

> RAG 的核心价值：**让模型基于你自己的最新数据回答，而不是凭记忆瞎编。**

## 小结

| 方案 | 适用场景 | 复杂度 |
|------|----------|--------|
| Prompt | 通用问答 | ⭐ |
| 函数调用 | 需要外部数据/动作 | ⭐⭐ |
| RAG | 私域知识库问答 | ⭐⭐⭐ |

下一篇会手写一个最小可用的 RAG 管线，敬请期待。
