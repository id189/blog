#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI HOT 日报晨报仪表盘生成器
- 调 daily 接口（带回退到最近一期）拉五版块精选
- 调 items 接口按 id 匹配补充 publishedAt（日报本身无逐条时间）
- 生成一篇带完整 frontmatter 的 Astro 博客 Markdown 文章（响应式仪表盘）
用法: python ai-daily-generator.py [--date YYYY-MM-DD] [--out 输出路径]
"""
import argparse
import html
import json
import subprocess
import sys
from datetime import datetime, timedelta

BASE = "https://aihot.virxact.com/api/public"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

# 五个固定版块（顺序固定；用 label 与日报 sections 对齐）
CANON = [
    "模型发布/更新",
    "产品发布/更新",
    "行业动态",
    "论文研究",
    "技巧与观点",
]
WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


def curl_json(url: str):
    """带浏览器 UA 调 API，返回解析后的 dict；失败返回 None。"""
    try:
        out = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "30", "-H", f"User-Agent: {UA}", url],
            capture_output=True, text=True, timeout=40,
        )
    except Exception as e:
        print(f"[warn] curl 调用失败: {e}", file=sys.stderr)
        return None
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout)
    except Exception:
        return None


def get_daily(target: str):
    """返回 (data, used_date)。当日无则回退最近一期。"""
    data = curl_json(f"{BASE}/daily/{target}")
    if data and data.get("sections"):
        return data, target
    lst = curl_json(f"{BASE}/dailies?take=1")
    if lst and lst.get("items"):
        latest = lst["items"][0]["date"]
        data2 = curl_json(f"{BASE}/daily/{latest}")
        if data2 and data2.get("sections"):
            print(f"[info] 当日({target})日报缺失，已回退到最近一期 {latest}", file=sys.stderr)
            return data2, latest
    raise SystemExit("无法获取日报数据（daily / dailies 均失败）")


def get_items_map(window_start: str):
    """按 id -> publishedAt 建表（日报 permalink 末段即 id）。"""
    m = {}
    since = window_start
    url = f"{BASE}/items?mode=all&since={since}&take=100"
    pages = 0
    while url and pages < 5:
        pages += 1
        d = curl_json(url)
        if not d or "items" not in d:
            break
        for it in d["items"]:
            if it.get("id") and it.get("publishedAt"):
                m[it["id"]] = it["publishedAt"]
        if d.get("hasNext") and d.get("nextCursor"):
            url = f"{BASE}/items?mode=all&since={since}&take=100&cursor={d['nextCursor']}"
        else:
            url = None
    return m


def humanize(pub_iso, report_date):
    """北京时间人话；绝不出现 ISO。"""
    if not pub_iso:
        return "近日"
    try:
        dt = datetime.fromisoformat(pub_iso.replace("Z", "+00:00"))
    except Exception:
        return "近日"
    bj = dt + timedelta(hours=8)
    bj_date = bj.date()
    if bj_date == report_date:
        prefix = "今天"
    elif bj_date == report_date - timedelta(days=1):
        prefix = "昨天"
    else:
        prefix = f"{bj_date.month}月{bj_date.day}日"
    return f"{prefix} {bj.hour:02d}:{bj.minute:02d}"


def trunc(s, n=60):
    s = (s or "").strip()
    if len(s) <= n:
        return s
    return s[: n - 1] + "…"


def build(out_path: str, target_date: str):
    data, used_date = get_daily(target_date)
    window_start = data.get("windowStart")
    items_map = get_items_map(window_start) if window_start else {}

    report_date = datetime.strptime(used_date, "%Y-%m-%d").date()
    report_human = f"{report_date.year}年{report_date.month}月{report_date.day}日"
    weekday = WEEKDAYS[report_date.weekday()]
    canonical = data.get("attribution", {}).get("canonical", f"{BASE.replace('/api/public','')}/daily/{used_date}")

    # 按固定顺序对齐版块
    by_label = {s.get("label"): s for s in data.get("sections", [])}
    ordered = [(lbl, by_label.get(lbl, {"label": lbl, "items": []})) for lbl in CANON]

    # 全局连续编号
    global_num = 0
    sections_html = []
    nav_html = []
    stats_html = []
    total = 0

    for idx, (label, sec) in enumerate(ordered, start=1):
        items = sec.get("items", []) or []
        count = len(items)
        total += count
        sec_id = f"sec-{idx}"

        # 锚点导航
        nav_html.append(
            f'<a class="ad-nav-link" href="#{sec_id}">{html.escape(label)} <b>{count}</b></a>'
        )
        # Hero 统计
        stats_html.append(
            f'<div class="ad-stat"><span class="ad-stat-n">{count}</span>'
            f'<span class="ad-stat-l">{html.escape(label)}</span></div>'
        )

        cards = []
        for it in items:
            global_num += 1
            num = global_num
            title = html.escape(it.get("title", ""))
            summary = html.escape(trunc(it.get("summary", ""), 60))
            source = html.escape(it.get("sourceName", "未知来源"))
            link = it.get("sourceUrl") or it.get("permalink") or "#"
            link = html.escape(link)
            item_id = (it.get("permalink") or "").rsplit("/", 1)[-1]
            pub = items_map.get(item_id)
            time_h = humanize(pub, report_date)
            cards.append(
                f'<article class="ad-card">'
                f'<div class="ad-card-top"><span class="ad-num">{num}</span>'
                f'<span class="ad-time">🕒 {time_h}</span></div>'
                f'<h3 class="ad-title"><a href="{link}" target="_blank" rel="noopener noreferrer">{title}</a></h3>'
                f'<div class="ad-meta"><span class="ad-chip">{source}</span></div>'
                f'<p class="ad-summary">{summary}</p>'
                f'<a class="ad-link" href="{link}" target="_blank" rel="noopener noreferrer">阅读原文 →</a>'
                f"</article>"
            )

        grid = "".join(cards)
        sections_html.append(
            f'<section class="ad-section" id="{sec_id}">'
            f'<h2 class="ad-h2"><span class="ad-h2-label">{html.escape(label)}</span>'
            f'<span class="ad-h2-count">{count} 条</span></h2>'
            f'<div class="ad-grid">{grid}</div></section>'
        )

    # 数据窗口人话
    try:
        ws = datetime.fromisoformat((window_start or "").replace("Z", "+00:00")) + timedelta(hours=8)
        we = datetime.fromisoformat((data.get("windowEnd") or "").replace("Z", "+00:00")) + timedelta(hours=8)
        window_human = f"{ws.month}月{ws.day}日 {ws.hour:02d}:{ws.minute:02d} – {we.month}月{we.day}日 {we.hour:02d}:{we.minute:02d}（北京时间）"
    except Exception:
        window_human = "详见来源"

    hero = (
        f'<header class="ad-hero">'
        f'<div class="ad-hero-date">{report_human} · {weekday}</div>'
        f'<h1 class="ad-hero-title">🤖 AI 日报晨报</h1>'
        f'<div class="ad-hero-sub">AI HOT 精选 · 共 <b>{total}</b> 条要闻 · 五大版块速览</div>'
        f'<div class="ad-stats">' + "".join(stats_html) + '</div>'
        f'<div class="ad-hero-note">数据窗口：{window_human} ｜ 来源：AI HOT</div>'
        f"</header>"
    )
    nav = f'<nav class="ad-nav">{"".join(nav_html)}</nav>'
    body_sections = "".join(sections_html)
    footer = (
        f'<footer class="ad-footer">'
        f'<div>本期共 <b>{total}</b> 条 · 数据来源：'
        f'<a href="{html.escape(canonical)}" target="_blank" rel="noopener noreferrer">AI HOT</a>'
        f'（aihot.virxact.com）</div>'
        f'<div class="ad-footer-note">由 AI HOT 日报接口自动生成 · 时间为北京时间</div>'
        f"</footer>"
    )

    frontmatter = (
        "---\n"
        f'title: "AI 日报晨报 · {report_human}"\n'
        f'description: "AI HOT 今日精选：模型/产品/行业/论文/技巧五大版块共 {total} 条要闻，一键速览。"\n'
        f"date: {used_date}\n"
        'tags: ["AI日报", "大模型", "AI产品"]\n'
        'category: "AI 应用"\n'
        'emoji: "🤖"\n'
        'cover: ""\n'
        'author: "你的名字"\n'
        "draft: false\n"
        "---\n"
    )

    doc = (
        frontmatter + "\n"
        + '<div class="ai-daily">\n'
        + "<style>" + CSS + "</style>\n\n"
        + hero + "\n\n" + nav + "\n\n" + body_sections + "\n\n" + footer + "\n"
        + "</div>\n"
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"[ok] 已生成 {out_path}（{used_date}，共 {total} 条，全局编号 1..{global_num}）")


CSS = """
.ai-daily, .ai-daily * { box-sizing: border-box; }
.ai-daily h1, .ai-daily h2, .ai-daily h3, .ai-daily p, .ai-daily a,
.ai-daily div, .ai-daily section, .ai-daily nav, .ai-daily header,
.ai-daily footer, .ai-daily article, .ai-daily span {
  margin: 0; padding: 0; font-weight: normal; text-decoration: none;
  color: inherit; background: none; border: 0; line-height: 1.6;
}
.ai-daily {
  --accent: #4f46e5; --accent2: #0ea5e9; --bg: #f5f7fb; --card: #ffffff;
  --border: #e6e8ef; --text: #1f2430; --muted: #6b7280;
  max-width: 100%; color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}
.ai-daily a { color: var(--accent); }
.ai-daily h2.ad-h2 { scroll-margin-top: 24px; }

/* Hero */
.ad-hero {
  background: linear-gradient(135deg, #4f46e5 0%, #0ea5e9 100%);
  color: #fff; border-radius: 18px; padding: 28px 28px 22px; margin-bottom: 18px;
  box-shadow: 0 10px 30px rgba(79,70,229,.18);
}
.ad-hero-date { font-size: 14px; opacity: .92; letter-spacing: .5px; }
.ad-hero-title { font-size: 30px; font-weight: 800; margin: 6px 0 8px; }
.ad-hero-sub { font-size: 15px; opacity: .95; }
.ad-hero-sub b { font-weight: 800; }
.ad-stats { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }
.ad-stat {
  background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.28);
  border-radius: 12px; padding: 10px 14px; min-width: 92px; text-align: center;
  backdrop-filter: blur(4px);
}
.ad-stat-n { display: block; font-size: 22px; font-weight: 800; line-height: 1.2; }
.ad-stat-l { display: block; font-size: 12px; opacity: .9; margin-top: 2px; }
.ad-hero-note { margin-top: 14px; font-size: 12px; opacity: .85; }

/* Nav */
.ad-nav { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 22px; }
.ad-nav-link {
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--card); border: 1px solid var(--border); border-radius: 999px;
  padding: 8px 14px; font-size: 13px; color: var(--text); transition: .15s;
}
.ad-nav-link:hover { border-color: var(--accent); color: var(--accent); transform: translateY(-1px); }
.ad-nav-link b { color: var(--accent); font-weight: 800; }

/* Section */
.ad-section { margin-bottom: 28px; }
.ad-h2 {
  display: flex; align-items: baseline; gap: 10px; font-size: 20px; font-weight: 800;
  padding-bottom: 10px; margin-bottom: 16px; border-bottom: 2px solid var(--border);
}
.ad-h2-count { font-size: 13px; font-weight: 600; color: var(--muted); }

/* Grid */
.ad-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }
.ad-card {
  background: var(--card); border: 1px solid var(--border); border-radius: 14px;
  padding: 16px; display: flex; flex-direction: column; gap: 8px;
  transition: .18s; box-shadow: 0 1px 3px rgba(16,24,40,.04);
}
.ad-card:hover { transform: translateY(-3px); box-shadow: 0 10px 24px rgba(16,24,40,.10); border-color: #c9cdfb; }
.ad-card-top { display: flex; justify-content: space-between; align-items: center; }
.ad-num {
  display: inline-flex; align-items: center; justify-content: center;
  width: 26px; height: 26px; border-radius: 8px; background: var(--accent);
  color: #fff; font-size: 13px; font-weight: 800;
}
.ad-time { font-size: 12px; color: var(--muted); }
.ad-title { font-size: 15.5px; font-weight: 700; line-height: 1.45; }
.ad-title a { color: var(--text); }
.ad-title a:hover { color: var(--accent); }
.ad-meta { display: flex; gap: 8px; flex-wrap: wrap; }
.ad-chip {
  display: inline-block; background: #eef0fe; color: #4338ca;
  border-radius: 999px; padding: 3px 10px; font-size: 12px; font-weight: 600;
}
.ad-summary { font-size: 13.5px; color: #374151; line-height: 1.6; }
.ad-link {
  margin-top: auto; align-self: flex-start; font-size: 13px; font-weight: 700;
  color: var(--accent); border: 1px solid var(--border); border-radius: 8px;
  padding: 6px 12px; transition: .15s;
}
.ad-link:hover { background: var(--accent); color: #fff; border-color: var(--accent); }

/* Footer */
.ad-footer {
  margin-top: 26px; padding: 18px 20px; border-top: 2px dashed var(--border);
  font-size: 13px; color: var(--muted); display: flex; flex-direction: column; gap: 4px;
}
.ad-footer b { color: var(--text); font-weight: 800; }
.ad-footer-note { font-size: 12px; opacity: .8; }
"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="目标日报日期 YYYY-MM-DD")
    ap.add_argument(
        "--out",
        default=r"D:\OneDrive\桌面\WorkBuddy\blog\src\content\posts\2026-07-12-ai-daily.md",
        help="输出 Markdown 路径",
    )
    args = ap.parse_args()
    # 输出文件名跟随实际使用的日期，保证可复现
    if args.date and "2026-07-12" in args.out:
        pass
    build(args.out, args.date)
