#!/usr/bin/env python3
"""Build index.html from deals.json.

The page is a static Amazon Associates catalog. It never calls an API,
never reads a secret, and never invents a price or a discount.
"""

from __future__ import annotations

import json
import re
import sys
from html import escape
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent
DEALS_PATH = ROOT / "deals.json"
INDEX_PATH = ROOT / "index.html"

ASSOCIATE_TAG = "issac03-20"
ASIN_RE = re.compile(r"^[A-Z0-9]{10}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FILE_KEYS = {"associate_tag", "curated_on", "deals"}
DEAL_KEYS = {"title", "asin", "category", "blurb"}
BANNED_COPY = ("折扣", "限時", "半價", "促銷", "%", " OFF")

PAGE = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Issac's Picks — Amazon products</title>
  <meta name="description" content="Hand-picked Amazon products from Chun Hin (Issac). Links use affiliate tag issac03-20. No invented discounts — check Amazon for the current price. 手動挑選的 Amazon 商品，不編造折扣。">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%23241c16'/%3E%3Ctext x='16' y='22' text-anchor='middle' font-size='16' fill='%23f6f1e8' font-family='Georgia'>%3CI%3C/text%3E%3C/svg%3E">
  <script>
    (function () {
      try {
        var q = new URLSearchParams(location.search).get("lang");
        var saved = localStorage.getItem("issac-picks-lang");
        var lang = q === "en" || q === "zh-Hant" ? q : saved;
        if (lang === "en" || lang === "zh-Hant") document.documentElement.lang = lang;
      } catch (e) {}
    })();
  </script>
  <style>
    :root {
      --ink: #241c16;
      --muted: #6b5e53;
      --paper: #f3eee6;
      --card: #fffcf8;
      --line: #e3d9cc;
      --accent: #9a4318;
      --note: #fff6e8;
      --note-line: #e6c48a;
      --shadow: 0 10px 30px rgba(36, 28, 22, 0.06);
      color-scheme: light;
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(1200px 480px at 10% -10%, #efe2cf 0%, transparent 55%),
        var(--paper);
      font-family: "Avenir Next", "Segoe UI", "PingFang TC", "Noto Sans TC", "Microsoft JhengHei", "WenQuanYi Micro Hei", sans-serif;
      line-height: 1.6;
    }
    html[lang="en"] .lang-zh { display: none !important; }
    html[lang="zh-Hant"] .lang-en { display: none !important; }
    a { color: inherit; }
    .skip {
      position: absolute;
      left: 1rem;
      top: -4rem;
      background: var(--ink);
      color: var(--paper);
      padding: 0.5rem 0.8rem;
      border-radius: 8px;
      z-index: 5;
    }
    .skip:focus { top: 0.75rem; }
    .wrap { width: min(1080px, calc(100% - 2rem)); margin: 0 auto; }
    .site-header {
      position: sticky;
      top: 0;
      z-index: 4;
      background: rgba(243, 238, 230, 0.92);
      backdrop-filter: blur(10px);
      border-bottom: 1px solid var(--line);
    }
    .header-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      min-height: 4.25rem;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      text-decoration: none;
    }
    .mark {
      width: 2.25rem;
      height: 2.25rem;
      display: grid;
      place-items: center;
      border-radius: 8px;
      background: var(--ink);
      color: #f6f1e8;
      font-family: Georgia, "Songti TC", "PMingLiU", serif;
      font-weight: 700;
    }
    .brand-name { display: block; font-weight: 700; letter-spacing: -0.02em; }
    .brand-sub { display: block; color: var(--muted); font-size: 0.82rem; }
    .lang-toggle {
      display: inline-flex;
      padding: 0.2rem;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: var(--card);
    }
    .lang-toggle button, .filters button {
      font: inherit;
      cursor: pointer;
      border: 0;
      background: transparent;
      color: var(--ink);
    }
    .lang-toggle button {
      border-radius: 999px;
      padding: 0.35rem 0.8rem;
    }
    .lang-toggle button[aria-pressed="true"], .filters button[aria-pressed="true"] {
      background: var(--ink);
      color: #f6f1e8;
    }
    .hero { padding: 2.5rem 0 1rem; }
    h1 {
      margin: 0 0 0.6rem;
      font-family: Georgia, "Iowan Old Style", "Songti TC", "PMingLiU", "WenQuanYi Micro Hei", serif;
      font-size: clamp(2rem, 4.4vw, 3.4rem);
      font-weight: 600;
      letter-spacing: -0.03em;
      line-height: 1.15;
    }
    .lede { max-width: 42rem; margin: 0; color: var(--muted); font-size: 1.05rem; }
    .disclosure {
      margin: 1.5rem 0 0;
      padding: 1rem 1.1rem;
      background: var(--note);
      border: 1px solid var(--note-line);
      border-radius: 16px;
    }
    .disclosure-kicker {
      margin: 0 0 0.4rem;
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--accent);
    }
    .disclosure p { margin: 0.45rem 0 0; }
    .filters { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1.25rem 0 0; }
    .filters button {
      border: 1px solid var(--line);
      background: var(--card);
      border-radius: 999px;
      padding: 0.4rem 0.85rem;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1rem;
      padding: 1.25rem 0 3rem;
    }
    .card {
      display: flex;
      flex-direction: column;
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 1.15rem 1.15rem 1.05rem;
      box-shadow: var(--shadow);
      border-top: 4px solid var(--cat, var(--accent));
    }
    /* display:flex would otherwise override the hidden attribute */
    .card[hidden] { display: none !important; }
    .card[data-category="smart-home"] { --cat: #2f6f68; }
    .card[data-category="reading"] { --cat: #6d5a3a; }
    .card[data-category="streaming"] { --cat: #3d4f73; }
    .card[data-category="kitchen"] { --cat: #8a4b32; }
    .card[data-category="computers"] { --cat: #3e4a3a; }
    .card[data-category="charging"] { --cat: #8a6232; }
    .card[data-category="audio"] { --cat: #5a3d55; }
    .card[data-category="item-finders"] { --cat: #4a5560; }
    .category {
      margin: 0;
      color: var(--cat, var(--accent));
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }
    h2 { margin: 0.35rem 0 0.55rem; font-size: 1.18rem; line-height: 1.35; letter-spacing: -0.02em; }
    .blurb { margin: 0; color: #3f362f; }
    .meta { margin-top: auto; padding-top: 1rem; }
    .price-note { margin: 0 0 0.75rem; color: var(--muted); font-size: 0.92rem; }
    .asin { margin: 0 0 0.7rem; color: var(--muted); font-size: 0.78rem; letter-spacing: 0.04em; }
    .cta {
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 48px;
      border-radius: 999px;
      background: var(--ink);
      color: #f6f1e8;
      text-decoration: none;
      font-weight: 700;
    }
    .cta:hover { background: #3a2e25; }
    .site-footer {
      border-top: 1px solid var(--line);
      padding: 1.5rem 0 2.5rem;
      color: var(--muted);
      font-size: 0.92rem;
    }
    .site-footer p { margin: 0.4rem 0; }
    :focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }
    .sr-only {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }
    @media (prefers-reduced-motion: reduce) {
      html { scroll-behavior: auto; }
    }
  </style>
</head>
<body>
  <a class="skip" href="#products">Skip to products / 跳至商品</a>
  <header class="site-header">
    <div class="wrap header-row">
      <a class="brand" href="#top">
        <span class="mark" aria-hidden="true">I</span>
        <span>
          <span class="brand-name">Issac's Picks</span>
          <span class="brand-sub lang-zh" lang="zh-Hant">Amazon 聯盟精選</span>
          <span class="brand-sub lang-en" lang="en">Amazon Associates picks</span>
        </span>
      </a>
      <div class="lang-toggle" role="group" aria-label="Language / 語言">
        <button type="button" data-set-lang="zh-Hant" aria-pressed="true">中文</button>
        <button type="button" data-set-lang="en" aria-pressed="false">EN</button>
      </div>
    </div>
  </header>
  <main id="top">
    <div class="wrap hero">
      <h1>
        <span class="lang-zh" lang="zh-Hant">需求穩定的 Amazon 商品</span>
        <span class="lang-en" lang="en">Amazon products with steady demand</span>
      </h1>
      <p class="lede">
        <span class="lang-zh" lang="zh-Hant">Chun Hin（Issac）手動挑選的 @@COUNT@@ 項常見商品。這不是即時優惠清單，也沒有任何自行計算的折扣。</span>
        <span class="lang-en" lang="en">@@COUNT@@ widely used products, chosen by hand by Chun Hin (Issac). This is not a live deals feed, and no discount is calculated here.</span>
      </p>
      <aside class="disclosure" aria-label="Affiliate disclosure">
        <p class="disclosure-kicker">Affiliate disclosure · 聯盟行銷揭露</p>
        <p lang="en"><strong>As an Amazon Associate I earn from qualifying purchases.</strong> Chun Hin (Issac) earns a commission if you buy through a link on this page. Prices and discounts are not listed, because they change. Check Amazon for the current price, seller, and availability.</p>
        <p lang="zh-Hant"><strong>作為 Amazon 聯盟夥伴，我從符合資格的購買中獲得佣金。</strong>若你經由本頁連結購買，Chun Hin（Issac）可能獲得佣金。這裡不列出價格或折扣，因為它們會變動。請到 Amazon 查看即時價格、賣家與庫存。</p>
      </aside>
      <div class="filters" role="group" aria-label="Categories / 分類">
        @@FILTERS@@
      </div>
    </div>
    <div class="wrap grid" id="products">
      @@CARDS@@
    </div>
  </main>
  <footer class="site-footer">
    <div class="wrap">
      <p lang="en"><strong>As an Amazon Associate I earn from qualifying purchases.</strong> Tracking tag: issac03-20. List curated @@CURATED@@. This page does not check live prices.</p>
      <p lang="zh-Hant"><strong>作為 Amazon 聯盟夥伴，我從符合資格的購買中獲得佣金。</strong>追蹤標籤：issac03-20。清單整理日期：@@CURATED@@。本頁沒有查核即時價格。</p>
      <p>© @@YEAR@@ Chun Hin (Issac). Amazon and related marks are trademarks of Amazon.com, Inc. or its affiliates. This site is not operated by Amazon.</p>
    </div>
  </footer>
  <script>
    (function () {
      var key = "issac-picks-lang";
      var langButtons = document.querySelectorAll("[data-set-lang]");
      function applyLang(lang) {
        if (lang !== "en") lang = "zh-Hant";
        document.documentElement.lang = lang;
        langButtons.forEach(function (btn) {
          btn.setAttribute("aria-pressed", btn.getAttribute("data-set-lang") === lang ? "true" : "false");
        });
        try { localStorage.setItem(key, lang); } catch (e) {}
      }
      langButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
          applyLang(btn.getAttribute("data-set-lang"));
        });
      });
      applyLang(document.documentElement.lang === "en" ? "en" : "zh-Hant");

      var filters = document.querySelectorAll("[data-filter]");
      var cards = document.querySelectorAll(".card");
      function applyFilter(id) {
        filters.forEach(function (btn) {
          btn.setAttribute("aria-pressed", btn.getAttribute("data-filter") === id ? "true" : "false");
        });
        cards.forEach(function (card) {
          card.hidden = !(id === "all" || card.getAttribute("data-category") === id);
        });
      }
      filters.forEach(function (btn) {
        btn.addEventListener("click", function () { applyFilter(btn.getAttribute("data-filter")); });
      });
    })();
  </script>
</body>
</html>
"""


def with_associate_tag(url: str, tag: str) -> str:
    """Append tag with ? or &. An existing tag is replaced."""
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError(f"invalid product url: {url}")
    pairs = [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True) if key != "tag"]
    pairs.append(("tag", tag))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(pairs), parts.fragment))


def _self_test() -> None:
    tag = ASSOCIATE_TAG
    plain = with_associate_tag("https://www.amazon.com/dp/B00FLYWNYQ", tag)
    if plain != "https://www.amazon.com/dp/B00FLYWNYQ?tag=issac03-20":
        raise AssertionError(plain)
    extra = with_associate_tag("https://www.amazon.com/dp/B00FLYWNYQ?th=1", tag)
    if extra != "https://www.amazon.com/dp/B00FLYWNYQ?th=1&tag=issac03-20":
        raise AssertionError(extra)
    replaced = with_associate_tag("https://www.amazon.com/dp/B00FLYWNYQ?tag=old-20&psc=1", tag)
    if replaced != "https://www.amazon.com/dp/B00FLYWNYQ?psc=1&tag=issac03-20":
        raise AssertionError(replaced)


def _bilingual(value: object, label: str) -> tuple[str, str]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object with en and zh-Hant")
    english = str(value.get("en", "")).strip()
    chinese = str(value.get("zh-Hant", "")).strip()
    if not english or not chinese:
        raise ValueError(f"{label} needs both en and zh-Hant")
    for text in (english, chinese):
        for banned in BANNED_COPY:
            if banned in text:
                raise ValueError(f"{label} contains {banned!r}; this site does not state discounts")
    return english, chinese


def _slug(english_category: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", english_category.lower()).strip("-")
    if not slug:
        raise ValueError(f"cannot slug category {english_category!r}")
    return slug


def load_deals(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("deals.json must be an object")
    extra = set(data) - FILE_KEYS
    if extra:
        raise ValueError(f"unexpected deals.json keys: {sorted(extra)}")
    if data.get("associate_tag") != ASSOCIATE_TAG:
        raise ValueError(f"associate_tag must be {ASSOCIATE_TAG}")
    curated = data.get("curated_on")
    if not isinstance(curated, str) or not DATE_RE.fullmatch(curated):
        raise ValueError("curated_on must be YYYY-MM-DD")
    deals = data.get("deals")
    if not isinstance(deals, list) or not 8 <= len(deals) <= 12:
        raise ValueError("deals must be a list of 8 to 12 products")
    seen: set[str] = set()
    for index, deal in enumerate(deals, start=1):
        if not isinstance(deal, dict):
            raise ValueError(f"deal {index} must be an object")
        unexpected = set(deal) - DEAL_KEYS
        if unexpected:
            raise ValueError(f"deal {index} has unexpected keys {sorted(unexpected)}")
        missing = DEAL_KEYS - set(deal)
        if missing:
            raise ValueError(f"deal {index} is missing {sorted(missing)}")
        asin = str(deal["asin"]).strip()
        if not ASIN_RE.fullmatch(asin):
            raise ValueError(f"deal {index} has an invalid ASIN")
        if asin in seen:
            raise ValueError(f"duplicate ASIN {asin}")
        seen.add(asin)
        _bilingual(deal["title"], f"deal {index} title")
        _bilingual(deal["category"], f"deal {index} category")
        _bilingual(deal["blurb"], f"deal {index} blurb")
    return data


def _pair(english: str, chinese: str, tag: str = "span") -> str:
    return (
        f'<{tag} class="lang-zh" lang="zh-Hant">{escape(chinese)}</{tag}>'
        f'<{tag} class="lang-en" lang="en">{escape(english)}</{tag}>'
    )


def render_filters(deals: list[dict]) -> str:
    buttons = [
        '<button type="button" data-filter="all" aria-pressed="true">'
        '<span class="lang-zh" lang="zh-Hant">全部</span>'
        '<span class="lang-en" lang="en">All</span></button>'
    ]
    seen: list[tuple[str, str, str]] = []
    for deal in deals:
        english, chinese = _bilingual(deal["category"], "category")
        slug = _slug(english)
        if not any(item[0] == slug for item in seen):
            seen.append((slug, english, chinese))
    for slug, english, chinese in seen:
        buttons.append(
            f'<button type="button" data-filter="{escape(slug)}" aria-pressed="false">'
            f"{_pair(english, chinese)}</button>"
        )
    return "\n        ".join(buttons)


def render_card(deal: dict) -> str:
    title_en, title_zh = _bilingual(deal["title"], "title")
    category_en, category_zh = _bilingual(deal["category"], "category")
    blurb_en, blurb_zh = _bilingual(deal["blurb"], "blurb")
    asin = deal["asin"].strip()
    slug = _slug(category_en)
    url = with_associate_tag(f"https://www.amazon.com/dp/{asin}", ASSOCIATE_TAG)
    return f"""<article class="card" data-category="{escape(slug)}">
        <p class="category">{_pair(category_en, category_zh)}</p>
        <h2>{_pair(title_en, title_zh)}</h2>
        <p class="blurb">{_pair(blurb_en, blurb_zh)}</p>
        <div class="meta">
          <p class="price-note">{_pair("Check Amazon for the current price.", "請到 Amazon 查看即時價格。")}</p>
          <p class="asin">ASIN {escape(asin)}</p>
          <a class="cta" href="{escape(url)}" target="_blank" rel="nofollow sponsored noopener noreferrer">
            <span class="lang-zh" lang="zh-Hant">到 Amazon 查看<span class="sr-only">：{escape(title_zh)}</span></span>
            <span class="lang-en" lang="en">View on Amazon<span class="sr-only">: {escape(title_en)}</span></span>
          </a>
        </div>
      </article>"""


def render_page(data: dict) -> str:
    deals = data["deals"]
    cards = "\n      ".join(render_card(deal) for deal in deals)
    page = PAGE
    page = page.replace("@@COUNT@@", str(len(deals)))
    page = page.replace("@@CURATED@@", escape(data["curated_on"]))
    page = page.replace("@@YEAR@@", escape(data["curated_on"][:4]))
    page = page.replace("@@FILTERS@@", render_filters(deals))
    page = page.replace("@@CARDS@@", cards)
    if "@@" in page:
        raise ValueError("unreplaced template marker in index.html")
    return page


def validate_html(html: str, data: dict) -> None:
    hrefs = re.findall(r'href="(https://www\.amazon\.com/dp/[^"]+)"', html)
    expected = [
        f"https://www.amazon.com/dp/{deal['asin'].strip()}?tag={ASSOCIATE_TAG}"
        for deal in data["deals"]
    ]
    if hrefs != expected:
        raise ValueError(f"affiliate links do not match ASINs:\\n{hrefs}\\n{expected}")
    if html.count('rel="nofollow sponsored noopener noreferrer"') != len(expected):
        raise ValueError("every product link needs a sponsored rel")
    for banned in ("discount_percent", "APIFreeLLM", "GEMINI_API_KEY", "apf_", "generativeai", "% OFF", "省 "):
        if banned in html:
            raise ValueError(f"generated page still contains {banned!r}")


def main(argv: list[str]) -> int:
    _self_test()
    data = load_deals(DEALS_PATH)
    html = render_page(data)
    validate_html(html, data)
    if "--check" in argv:
        current = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.exists() else ""
        if current != html:
            print("index.html is out of date. Run: python3 generate_deals.py", file=sys.stderr)
            return 1
        print(f"index.html matches deals.json ({len(data['deals'])} products, tag {ASSOCIATE_TAG})")
        return 0
    INDEX_PATH.write_text(html, encoding="utf-8")
    print(f"Wrote {INDEX_PATH.name} with {len(data['deals'])} products tagged {ASSOCIATE_TAG}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
