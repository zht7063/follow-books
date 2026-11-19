#!/usr/bin/env python3
"""Build a finite Chinese sample reader from public records and original editorial."""
from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

if __package__:
    from .import_x_sample import read_json, require, validate_coverage, validate_sources
else:
    from import_x_sample import read_json, require, validate_coverage, validate_sources

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_FILE = 'chapters/begin-with-a-version.html'
# Exact previous generated files owned by this builder. Never recursively delete
# an arbitrary output directory or inspect private caches to discover content.
LEGACY_FILES = ('catalog.html', 'search-index.json', 'assets/search.js', 'assets/search-core.js') + tuple(
    f'chapters/{name}.html' for name in ('orientation', 'one-person-business', 'writing-and-attention',
                                      'ai-and-work', 'products-and-history', 'videos-unwatched', 'x-references'))


def esc(value):
    return html.escape(str(value), quote=True)


def load():
    sources = read_json(ROOT / 'data/thedankoe/sample-sources.json')
    coverage = read_json(ROOT / 'data/thedankoe/sample-coverage.json')
    chapter = read_json(ROOT / 'editorial/thedankoe/sample-chapter.json')
    validate_sources(sources)
    validate_coverage(coverage, sources)
    require(chapter['id'] == 'begin-with-a-version' and chapter['author'] == 'Engineer (bot)', 'Unexpected editorial')
    require([p['source_id'] for p in chapter['passages']] == [s['id'] for s in sources], 'Editorial must use exactly five sources in order')
    return sources, coverage, chapter


def shell(title, body, current):
    prefix = '../' if current == 'chapter' else ''
    links = [('index.html', '样章首页', 'home'), (CHAPTER_FILE, '01 · 开始与注意力', 'chapter'),
             ('coverage.html', '覆盖说明与编后记', 'coverage')]
    navigation = ''.join(f'<li><a href="{prefix}{url}"' + (' aria-current="page"' if key == current else '')
                         + f'>{esc(label)}</a></li>' for url, label, key in links)
    return f'''<!doctype html>
<html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; img-src 'self'; base-uri 'none'; form-action 'none'">
<meta name="referrer" content="no-referrer"><meta name="description" content="五条完整公开 X 短帖，一章原创中文编辑整理。非官方、未完成的连续阅读小样，等待用户审阅。">
<title>{esc(title)} · 从开始到专注 · Follow Books</title><link rel="stylesheet" href="{prefix}assets/reader.css">
</head><body><a class="skip" href="#main">跳到正文</a><div class="book">
<aside class="cover"><a class="brand" href="{prefix}index.html">follow books</a><p class="edition">Dan Koe · 中文阅读小样</p>
<p class="about-edition">从一个可以修改的版本开始，读到如何安放自己的时间与注意力。</p>
<nav class="contents" aria-label="阅读目录"><ul>{navigation}</ul></nav><p class="meta">非官方 · 小样 · 未完成<br>5 条短帖 / 1 章 · 等待审阅</p></aside>
<div class="leaf"><main id="main">{body}</main><footer>非官方、未完成的阅读小样（Unofficial sample）。中文编辑整理：Engineer (bot)。原帖作者：DAN KOE / @thedankoe。无隶属关系或背书（No affiliation or endorsement）。不是完整书籍或人物传记。交付后停止，等待用户审阅。</footer></div></div></body></html>'''


def source_note(source):
    s = source
    return f'''<div class="source-note" id="{esc(s['id'])}">
<p class="label">短引文 · 原文节选</p><blockquote lang="en"><p>{esc(s['quote'])}</p></blockquote>
<p class="label">来源</p><p class="meta"><a href="{esc(s['url'])}" rel="noreferrer">{esc(s['url'])}</a><br>
{esc(s['author']['name'])} / @{esc(s['author']['username'])} · 用户 ID {esc(s['author']['id'])}<br>
发表：<time datetime="{esc(s['created_at'])}">{esc(s['created_at_singapore'])}</time><br>
UTC：{esc(s['created_at'])} · 日期依据：官方 X API created_at（UTC）<br>
完整性：<span lang="en">{esc(s['completeness'])}</span>（完整短帖）· 已取得文字 {s['fetched_text_length']} 字符<br>
{esc(s['completeness_note'])}<br>{esc(s['conversation_completeness_note'])}<br>
取得依据：官方 {esc(s['provenance']['tool'])} · namespace {esc(s['provenance']['namespace'])} · 本地离线导入<br>
记录取得时间：{esc(s['provenance']['queried_at'])}</p>
<details><summary>查看校验与导入依据</summary><p class="meta">SHA-256（完整已取得文字的 UTF-8 字节）：<code>{esc(s['content_hash']['value'])}</code><br>
查询：<code>{esc(s['provenance']['query'])}</code> · max_results={s['provenance']['max_results']}<br>
本地依据：{esc(s['provenance']['response_file'])} + {esc(s['provenance']['selection_file'])}。原始响应不公开，构建器不读取原始缓存；哈希用于核对，不代表站点发布了全文。</p></details></div>'''


def exclusions_list(coverage):
    items = []
    for entry in coverage['exclusions']:
        detail = (f'《{esc(entry["title"])}》，plain_len {entry["plain_len"]}；' if 'title' in entry else '')
        items.append(f'<li><a href="{esc(entry["url"])}" rel="noreferrer">{esc(entry["post_id"])}</a>：{detail}{esc(entry["note"])}</li>')
    return '<ul class="exclusions">' + ''.join(items) + '</ul>'


def build(output=None):
    output = Path(output) if output is not None else ROOT / 'site'
    sources, coverage, chapter = load()  # Public inputs only; validate before writes.
    home = f'''<p class="eyebrow">原创中文编辑整理 · 连续阅读小样</p><h1>从开始到专注</h1>
<p class="deck">先给想法一个版本，再把时间与注意力留给它。</p>
<div class="notice"><p><strong>这是一个非官方、未完成的小样，不是完整书籍或人物传记。</strong>仅以五条完整公开 X 短帖为依据；中文由 Engineer (bot) 原创编写，与 Dan Koe 无隶属关系或背书。样章尚未获得用户视觉验收。</p></div>
<a class="primary" href="{CHAPTER_FILE}">进入样章 · 先做出一个版本</a>
<section class="prose"><h2>怎样读这一小章</h2><p>按五段编号顺读：开始带来经验，初稿允许不成熟，有了版本才有修改，投入时间也保留复查，最后回到正在被打断的事。段落之间有承接，段后有出处。</p>
<p>每段的“编辑整理”是独立的中文评论；“短引文”保留简短英文原句；“来源”列出作者、时区、完整性和取得依据。主题顺序不等于发表顺序，也不把独立短帖拼成作者的长文或串文。</p>
<h2>本次材料的边界</h2><p>此前一次官方 X 搜索取得 10 条结果，本样章选用其中 5 条完整短帖，长度分别为 68、266、263、277、205 字符。首次关键词查询返回 0 条，是成功空结果，不是 403/429 限制。本轮实现只读取本地文件，没有追加 X 请求。</p>
<p>另外五条未用于正文，原因如下：</p></section>{exclusions_list(coverage)}
<p class="meta">{esc(coverage['outside_sample'])} {esc(coverage['user_gate'])}</p>
<p><a href="coverage.html">阅读完整覆盖说明与编后记</a></p>'''
    parts = [f'<p class="eyebrow">样章 01 · 五段连续阅读</p><h1>{esc(chapter["title"])}</h1>',
             f'<p class="deck">{esc(chapter["framing"])}</p>',
             f'<p class="meta">中文编辑整理：{esc(chapter["author"])} · 编辑日期 {esc(chapter["edition_date"])}（非原帖发表日期）</p>']
    for number, (passage, source) in enumerate(zip(chapter['passages'], sources), 1):
        parts.append(f'<section class="passage" id="passage-{number}"><h2>{number:02} · {esc(passage["heading"])}</h2><p class="label">编辑整理</p><div class="prose">')
        parts.extend(f'<p>{esc(p)}</p>' for p in passage['paragraphs'])
        parts.append('</div>' + source_note(source) + '</section>')
    parts.append('<nav class="pager" aria-label="前后页"><a href="../index.html">上一页：样章首页</a><a href="../coverage.html">下一页：覆盖说明与编后记</a></nav>')
    colophon = f'''<p class="eyebrow">覆盖说明与编后记</p><h1>这五条以外，先留白</h1>
<div class="prose"><p>本样章只使用下面五条完整的独立短帖。完整性指单条已取得文字的范围和句末状态，不是整个账号、对话回复或思想体系完整。它们没有 note_post 长文内容，也未被视为串文。</p></div>
<ol class="source-register">{''.join(f'<li><a href="{CHAPTER_FILE}#{s["id"]}">{esc(s["id"])}</a> · {s["fetched_text_length"]} 字符 · {esc(s["created_at_singapore"])}</li>' for s in sources)}</ol>
<div class="prose"><h2>官方取得记录与排除项</h2><p>此前官方 x.search_posts_all，namespace x，无用户账户：首次关键词查询成功返回 0 条；一次修正查询 <code>{esc(coverage['corrective_search']['query'])}</code>，max_results=10，取得 10 条，选择 5 条。没有翻页或增加来源；本轮仅离线导入这些记录。</p>
<p>以下五条只保留必要的识别元数据与排除原因，不概括未取得的目标，也不补全截断句子：</p></div>{exclusions_list(coverage)}
<div class="prose"><h2>编辑与发布说明</h2><p>中文编辑整理及阅读路径由 Engineer (bot) 原创，示例、练习和解释属于编辑意见；原帖的简短英文引文单独标注。唯一全文引句是本身仅 68 字符的一句短帖，其余均只摘取一个短句。两篇长文没有转载，原始 API 响应不进入站点。</p>
<p>{esc(coverage['outside_sample'])} 先前的作者站抓取已停止；本次不恢复抓取，不请求作者站、视频或其他来源。日期依据是官方 created_at UTC 字段，再换算为 Asia/Singapore。</p>
<p>本页的组织只借鉴按序阅读、开篇说明范围与逐段可见出处的通用做法。文字、标题和阅读路径均为本次原创，没有复制参考读物的措辞或条目模板。</p>
<p><strong>这是非官方、未完成的小样，尚未获得用户视觉验收。</strong>{esc(coverage['user_gate'])} 本次只提交与推送代码；同一隔离预览项目的重新部署另行进行。</p></div>
<nav class="pager" aria-label="前后页"><a href="{CHAPTER_FILE}">上一页：样章正文</a><a href="index.html">返回：样章首页</a></nav>'''
    pages = {'index.html': shell('样章首页', home, 'home'),
             CHAPTER_FILE: shell(chapter['title'], ''.join(parts), 'chapter'),
             'coverage.html': shell('覆盖说明与编后记', colophon, 'coverage')}
    for name, content in pages.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')
    (output / 'assets').mkdir(exist_ok=True)
    shutil.copyfile(ROOT / 'web/reader.css', output / 'assets/reader.css')
    for name in LEGACY_FILES:
        (output / name).unlink(missing_ok=True)
    print('Built 3 Chinese reading pages from 5 public sample records; no raw cache used.')


if __name__ == '__main__':
    build()
