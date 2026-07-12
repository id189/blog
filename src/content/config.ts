import { defineCollection, z } from "astro:content";

// 文章集合（Content Collections）。在 src/content/posts/ 下新增一个 .md 即被自动收录，
// 列表页与 /posts/<slug> 详情页由构建时统一生成，无需手动登记。
const posts = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    tags: z.array(z.string()).default([]),
    category: z.string().default("未分类"),
    emoji: z.string().default("🚀"),
    cover: z.string().optional(),
    author: z.string().default("你的名字"),
    draft: z.boolean().default(false),
  }),
});

export const collections = { posts };
