"""content/ のデータから静的 HTML サイトを生成する。"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
STATIC_DIR = ROOT / "static"
REQUIRED_WORK_FIELDS = ("id", "title", "artist", "year", "category", "description")


@dataclass
class Work:
    id: str
    title: str
    artist: str
    year: int
    category: str
    description: str
    medium: str = ""
    size: str = ""
    color: str = "#999999"
    image: str = ""

    @property
    def url(self) -> str:
        return f"works/{self.id}.html"


@dataclass
class Site:
    title: str
    subtitle: str = ""
    lead: str = ""
    period: str = ""
    hours: str = ""
    venue: str = ""
    address: str = ""
    admission: str = ""
    about: list[str] = field(default_factory=list)
    contact: str = ""
    footer: str = ""


def load_site(content_dir: Path = CONTENT_DIR) -> Site:
    data = json.loads((content_dir / "site.json").read_text(encoding="utf-8"))
    return Site(**data)


def load_works(content_dir: Path = CONTENT_DIR) -> list[Work]:
    data = json.loads((content_dir / "works.json").read_text(encoding="utf-8"))
    works: list[Work] = []
    seen: set[str] = set()
    for i, item in enumerate(data):
        missing = [k for k in REQUIRED_WORK_FIELDS if not item.get(k)]
        if missing:
            raise ValueError(f"works.json の {i + 1} 件目に必須項目がありません: {', '.join(missing)}")
        if item["id"] in seen:
            raise ValueError(f"works.json の id が重複しています: {item['id']}")
        seen.add(item["id"])
        works.append(Work(**item))
    return works


# ---------------------------------------------------------------- HTML 部品

def e(value: object) -> str:
    return escape(str(value), quote=True)


def artwork(work: Work, prefix: str) -> str:
    """作品画像。image 未指定ならテーマカラーのプレースホルダーを表示する。"""
    if work.image:
        return f'<img src="{prefix}images/{e(work.image)}" alt="{e(work.title)}" loading="lazy">'
    return (
        f'<div class="placeholder" style="--c:{e(work.color)}" role="img" '
        f'aria-label="{e(work.title)}（画像準備中）"><span>{e(work.category)}</span></div>'
    )


def page(site: Site, title: str, body: str, prefix: str = "") -> str:
    full_title = title if title == site.title else f"{title} | {site.title}"
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{e(site.lead)}">
<title>{e(full_title)}</title>
<link rel="stylesheet" href="{prefix}style.css">
</head>
<body>
<header class="site-header">
  <a class="logo" href="{prefix}index.html">{e(site.title)}</a>
  <nav>
    <a href="{prefix}index.html#about">展覧会について</a>
    <a href="{prefix}index.html#works">作品</a>
    <a href="{prefix}index.html#info">開催概要</a>
  </nav>
</header>
<main>
{body}
</main>
<footer class="site-footer"><p>{e(site.footer)}</p></footer>
<script src="{prefix}main.js" defer></script>
</body>
</html>
"""


def render_index(site: Site, works: list[Work]) -> str:
    categories = sorted({w.category for w in works}, key=[w.category for w in works].index)
    filters = '<button class="filter is-active" data-filter="all">すべて</button>' + "".join(
        f'<button class="filter" data-filter="{e(c)}">{e(c)}</button>' for c in categories
    )
    cards = "\n".join(
        f"""    <li class="card" data-category="{e(w.category)}">
      <a href="{w.url}">
        <div class="thumb">{artwork(w, "")}</div>
        <div class="card-body">
          <h3>{e(w.title)}</h3>
          <p class="meta">{e(w.artist)}・{e(w.year)}</p>
          <span class="tag">{e(w.category)}</span>
        </div>
      </a>
    </li>"""
        for w in works
    )
    about = "".join(f"<p>{e(p)}</p>" for p in site.about)
    info_rows = [
        ("会期", site.period), ("開館時間", site.hours), ("会場", site.venue),
        ("所在地", site.address), ("入場料", site.admission),
    ]
    info = "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in info_rows if v)
    body = f"""<section class="hero">
  <p class="subtitle">{e(site.subtitle)}</p>
  <h1>{e(site.title)}</h1>
  <p class="lead">{e(site.lead)}</p>
  <p class="period">{e(site.period)}</p>
  <a class="button" href="#works">作品を見る</a>
</section>

<section id="about" class="section">
  <h2>展覧会について</h2>
  {about}
</section>

<section id="works" class="section">
  <h2>展示作品 <small>{len(works)} 点</small></h2>
  <div class="filters" role="group" aria-label="カテゴリで絞り込み">{filters}</div>
  <ul class="grid">
{cards}
  </ul>
</section>

<section id="info" class="section">
  <h2>開催概要</h2>
  <dl class="info">{info}</dl>
  <p>{e(site.contact)}</p>
</section>"""
    return page(site, site.title, body)


def render_work(site: Site, works: list[Work], index: int) -> str:
    w = works[index]
    prev_w = works[index - 1] if index > 0 else None
    next_w = works[index + 1] if index < len(works) - 1 else None
    details = [("作家", w.artist), ("制作年", w.year), ("カテゴリ", w.category),
               ("技法・素材", w.medium), ("サイズ", w.size)]
    dl = "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in details if v)
    prev_link = f'<a class="prev" href="{e(prev_w.id)}.html">← {e(prev_w.title)}</a>' if prev_w else "<span></span>"
    next_link = f'<a class="next" href="{e(next_w.id)}.html">{e(next_w.title)} →</a>' if next_w else "<span></span>"
    body = f"""<article class="work section">
  <p class="breadcrumb"><a href="../index.html#works">作品一覧</a> / {e(w.title)}</p>
  <div class="work-layout">
    <div class="work-image">{artwork(w, "../")}</div>
    <div class="work-text">
      <h1>{e(w.title)}</h1>
      <p class="description">{e(w.description)}</p>
      <dl class="info">{dl}</dl>
    </div>
  </div>
  <nav class="pager">{prev_link}<a href="../index.html#works">一覧へ</a>{next_link}</nav>
</article>"""
    return page(site, w.title, body, prefix="../")


# ---------------------------------------------------------------- ビルド

def build(out_dir: Path, content_dir: Path = CONTENT_DIR, static_dir: Path = STATIC_DIR) -> list[Path]:
    """サイトを out_dir に生成し、書き出した HTML のパス一覧を返す。"""
    site = load_site(content_dir)
    works = load_works(content_dir)

    if out_dir.exists():
        shutil.rmtree(out_dir)
    (out_dir / "works").mkdir(parents=True)
    shutil.copytree(static_dir, out_dir, dirs_exist_ok=True)
    images = content_dir / "images"
    if images.is_dir():
        shutil.copytree(images, out_dir / "images", ignore=shutil.ignore_patterns(".gitkeep"))

    written = [out_dir / "index.html"]
    written[0].write_text(render_index(site, works), encoding="utf-8")
    for i, w in enumerate(works):
        path = out_dir / w.url
        path.write_text(render_work(site, works, i), encoding="utf-8")
        written.append(path)
    return written
