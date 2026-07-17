import type { APIRoute, GetStaticPaths } from "astro";
import { getCollection } from "astro:content";

interface RawNode {
  display: string;            // 该层级的原始展示名
  fullPath: string;           // 小写化、"/" 连接的完整路径（用于筛选前缀匹配）
  children: Map<string, RawNode>;
  direct: number;             // 恰好落在该节点的文章数
  subtree?: number;           // 子树文章总数
}

export const getStaticPaths: GetStaticPaths = async () => {
  const posts = await getCollection("posts", ({ data }) => !data.draft);
  const root: RawNode = { display: "", fullPath: "", children: new Map(), direct: 0 };

  for (const p of posts) {
    const segs = (p.data.category || "未分类")
      .split("/")
      .map((s) => s.trim())
      .filter(Boolean);
    let node = root;
    let path = "";
    for (const seg of segs) {
      const lower = seg.toLowerCase();
      path = path ? path + "/" + lower : lower;
      if (!node.children.has(lower)) {
        node.children.set(lower, {
          display: seg,
          fullPath: path,
          children: new Map(),
          direct: 0,
        });
      }
      node = node.children.get(lower)!;
    }
    node.direct += 1;
  }

  const count = (n: RawNode): number => {
    let t = n.direct;
    for (const c of n.children.values()) t += count(c);
    n.subtree = t;
    return t;
  };
  count(root);

  // 节点 id：用 "---" 替掉 "/" 得到单段标识（避免 "/" 被当成子路径，也规避 Windows 路径符号问题）。
  // 注意：params 必须返回「原始」段，URL 编码交由 Astro / 浏览器处理，切勿预 encodeURIComponent。
  const toId = (fullPath: string) => fullPath.replace(/\//g, "---") || "root";

  const ser = (n: RawNode) => ({
    id: toId(n.fullPath),
    name: n.display,
    path: n.fullPath,
    hasChildren: n.children.size > 0,
    postCount: n.subtree ?? 0,
    children: [...n.children.values()]
      .sort((a, b) => (b.subtree ?? 0) - (a.subtree ?? 0))
      .map((c) => ({
        id: toId(c.fullPath),
        name: c.display,
        path: c.fullPath,
        hasChildren: c.children.size > 0,
        postCount: c.subtree ?? 0,
      })),
  });

  const out: { params: { id: string }; props: { node: ReturnType<typeof ser> } }[] = [];
  const walk = (n: RawNode) => {
    out.push({ params: { id: toId(n.fullPath) }, props: { node: ser(n) } });
    for (const c of n.children.values()) walk(c);
  };
  walk(root);
  return out;
};

export const GET: APIRoute = ({ props }) => {
  return new Response(JSON.stringify((props as { node: unknown }).node), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
};
