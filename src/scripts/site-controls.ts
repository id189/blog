// 客户端 i18n + 主题切换 + 控件绑定（被 Vite 处理的模块脚本）
import { LANGS, DEFAULT_LANG, LANG_LOCALE, t } from "../i18n/ui";

const THEME_KEY = "theme";
const LANG_KEY = "lang";
const DEFAULT_THEME = "cute";
const THEMES = ["neon", "cute", "pretty", "cool"];
const THEME_ICONS: Record<string, string> = {
  neon: "◆",
  cute: "🌸",
  pretty: "💐",
  cool: "🌌",
};

function dictFor(lang: string) {
  return t[lang] || t[DEFAULT_LANG];
}

export function applyLang(lang: string) {
  const dict = dictFor(lang);
  document.documentElement.lang = lang;
  (window as any).__currentLang = lang;

  // 文本节点
  document.querySelectorAll<HTMLElement>("[data-i18n]").forEach((el) => {
    const k = el.dataset.i18n;
    if (!k) return;
    let v: string | undefined = dict[k];
    if (v == null) v = t[DEFAULT_LANG][k];
    if (v == null) return;
    if (el.dataset.count != null) v = v.replace("{n}", el.dataset.count);
    el.textContent = v;
  });

  // 属性节点（placeholder / aria-label 等）
  document.querySelectorAll<HTMLElement>("[data-i18n-attr]").forEach((el) => {
    const spec = el.dataset.i18nAttr;
    if (!spec) return;
    spec.split("|").forEach((pair) => {
      const [attr, key] = pair.split(":");
      let v: string | undefined = dict[key];
      if (v == null) v = t[DEFAULT_LANG][key];
      if (v != null) el.setAttribute(attr, v);
    });
  });

  // 日期重格式化
  const loc = LANG_LOCALE[lang] || "zh-CN";
  document.querySelectorAll<HTMLElement>("[data-iso]").forEach((el) => {
    const iso = el.dataset.iso;
    if (!iso) return;
    const d = new Date(iso);
    if (!isNaN(d.getTime())) {
      el.textContent = d.toLocaleDateString(loc, { year: "numeric", month: "long", day: "numeric" });
    }
  });

  // document.title 重建
  const titleEl = document.querySelector("title");
  if (titleEl) {
    const tpl = titleEl.dataset.tpl || "{site.title} · {site.tagline}";
    const pageKey = titleEl.dataset.pageKey || "";
    const pageText = pageKey
      ? dict[pageKey] || t[DEFAULT_LANG][pageKey] || titleEl.dataset.page || ""
      : titleEl.dataset.page || "";
    document.title = tpl
      .replace("{page}", pageText)
      .replace("{site.title}", dict["site.title"] || "")
      .replace("{site.tagline}", dict["site.tagline"] || "");
  }

  // meta description
  const metaDesc = document.querySelector('meta[name="description"]');
  if (metaDesc) {
    const key = metaDesc.getAttribute("data-desc-key");
    if (key) {
      const v = dict[key] || t[DEFAULT_LANG][key];
      if (v) metaDesc.setAttribute("content", v);
    }
  }

  localStorage.setItem(LANG_KEY, lang);

  // 语言按钮显示当前语言
  const langBtn = document.getElementById("langBtn");
  const cur = LANGS.find((l) => l.code === lang);
  if (langBtn && cur) {
    const curEl = langBtn.querySelector(".lang-cur");
    if (curEl) curEl.textContent = `${cur.flag} ${cur.label}`;
  }
  document.querySelectorAll<HTMLElement>(".lang-opt").forEach((el) => {
    el.classList.toggle("active", el.dataset.lang === lang);
  });
  updateThemeTrigger();
}

export function applyTheme(name: string) {
  // 随机：在上次主题之外挑一个，避免连续两次相同
  if (name === "random") {
    const last = document.documentElement.dataset.theme || DEFAULT_THEME;
    const pool = THEMES.filter((x) => x !== last);
    name = pool[Math.floor(Math.random() * pool.length)] || THEMES[0];
  }
  if (!THEMES.includes(name)) name = DEFAULT_THEME;
  document.documentElement.dataset.theme = name;
  localStorage.setItem(THEME_KEY, name);
  updateThemeTrigger();
  document.querySelectorAll<HTMLElement>(".theme-opt").forEach((el) => {
    el.classList.toggle("active", el.dataset.theme === name);
  });
}

// 根据当前主题更新导航栏“风格”下拉触发按钮的图标+文案（随语言切换而刷新）
function updateThemeTrigger() {
  const theme = document.documentElement.dataset.theme || DEFAULT_THEME;
  const lang = (window as any).__currentLang || DEFAULT_LANG;
  const dict = dictFor(lang);
  const btn = document.getElementById("themeBtn");
  const cur = btn?.querySelector(".theme-cur");
  if (cur) {
    const icon = THEME_ICONS[theme] ?? "◆";
    const label = dict["theme." + theme] || theme;
    cur.textContent = `${icon} ${label}`;
  }
}

// 供 index.astro 内联脚本调用的计数格式化
(window as any).__currentLang = DEFAULT_LANG;
(window as any).__fmtCount = (n: number) => {
  const lang = (window as any).__currentLang || DEFAULT_LANG;
  const dict = dictFor(lang);
  return (dict["index.count"] || "{n} 篇 · 持续更新中").replace("{n}", String(n));
};

function init() {
  applyTheme(localStorage.getItem(THEME_KEY) || DEFAULT_THEME);
  applyLang(localStorage.getItem(LANG_KEY) || DEFAULT_LANG);

  // 语言下拉
  const langBtn = document.getElementById("langBtn");
  const langMenu = document.getElementById("langMenu");
  langBtn?.addEventListener("click", (e) => {
    e.stopPropagation();
    langMenu?.classList.toggle("open");
  });
  document.querySelectorAll<HTMLElement>(".lang-opt").forEach((el) => {
    el.addEventListener("click", () => {
      applyLang(el.dataset.lang || DEFAULT_LANG);
      langMenu?.classList.remove("open");
    });
  });
  document.addEventListener("click", () => {
    langMenu?.classList.remove("open");
    themeMenu?.classList.remove("open");
    themeBtn?.setAttribute("aria-expanded", "false");
  });

  // 主题下拉
  const themeBtn = document.getElementById("themeBtn");
  const themeMenu = document.getElementById("themeMenu");
  themeBtn?.addEventListener("click", (e) => {
    e.stopPropagation();
    const open = themeMenu?.classList.toggle("open");
    themeBtn.setAttribute("aria-expanded", open ? "true" : "false");
  });
  document.querySelectorAll<HTMLElement>(".theme-opt").forEach((el) => {
    el.addEventListener("click", () => {
      applyTheme(el.dataset.theme || DEFAULT_THEME);
      themeMenu?.classList.remove("open");
      themeBtn?.setAttribute("aria-expanded", "false");
    });
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
