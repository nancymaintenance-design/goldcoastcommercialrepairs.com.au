"""Gold Coast V4 detail-body renderer; no header, footer, routes or deployment side effects."""
from html import escape
from pathlib import Path
import json

KINDS = {'service': 'services', 'sector': 'sectors', 'article': 'news'}


def e(value):
    return escape(str(value), quote=True)


def t(value, lang):
    return value.get(lang, '') if isinstance(value, dict) else str(value or '')


def bi(en, zh, lang):
    return en if lang == 'en' else zh


def load_catalog(content_dir):
    base = Path(content_dir)
    groups = [('service', 'services'), ('sector', 'sectors'), ('article', 'articles')]
    if base.is_file():
        content = json.loads(base.read_text(encoding='utf-8'))
        return {
            kind: {
                record['slug']: {**record, 'title': record.get('detailTitle', record['title'])}
                for record in content[group]
            }
            for kind, group in groups
        }
    return {
        kind: {record['slug']: record for record in json.loads((base / f'{group}.json').read_text(encoding='utf-8'))}
        for kind, group in groups
    }


def load_sources(content_dir):
    base = Path(content_dir)
    if base.is_file():
        records = json.loads(base.read_text(encoding='utf-8'))['referenceSources']
    else:
        records = json.loads((base / 'sources.json').read_text(encoding='utf-8'))
    return {record['id']: record for record in records}


def production_link(kind, slug, lang):
    return ('/zh' if lang == 'zh' else '') + '/' + KINDS[kind] + '/' + slug + '/'


IMAGE_MAP = {
    'building-maintenance': 'coastal-maintenance-editorial.png',
    'roofing-waterproofing': 'coastal-roof-editorial.png',
    'electrical-lighting': 'sector-office.jpg',
    'plumbing-drainage-gas': 'sector-hospitality.jpg',
    'hvac-building-systems': 'sector-office.jpg',
    'fire-security-access': 'coastal-maintenance-editorial.png',
    'landscaping-irrigation': 'sector-hospitality.jpg',
    'signage-wayfinding': 'sector-hospitality.jpg',
    'facade-high-access-cleaning': 'sector-hotel.jpg',
    'cleaning-waste-hygiene': 'sector-office.jpg',
    'car-parks-external-works': 'sector-industrial.jpg',
    'fit-outs-make-good': 'coastal-maintenance-editorial.png',
    'hotels-resorts': 'coastal-resort-editorial.png',
    'apartments-body-corporate': 'sector-hotel.jpg',
    'restaurants-cafes': 'sector-hospitality.jpg',
    'retail-shopping-centres': 'coastal-maintenance-editorial.png',
    'offices-mixed-use': 'sector-office.jpg',
    'warehouses-logistics': 'sector-industrial.jpg',
    'workshops-industrial': 'sector-workshop.jpg',
    'education-healthcare-community': 'sector-healthcare.jpg',
    'salt-air-coastal-building-maintenance': 'coast-hero.webp',
    'storm-season-roofs-gutters': 'coastal-roof-editorial.png',
    'hotel-maintenance-between-guest-stays': 'coastal-resort-editorial.png',
    'body-corporate-common-area-repairs': 'coastal-maintenance-editorial.png',
    'outdoor-dining-paving-drainage': 'sector-hospitality.jpg',
    'tracking-commercial-water-ingress': 'sector-hotel.jpg',
}


def image_dimensions(name):
    if name.startswith('sector-'):
        return (1080, 608 if name in {'sector-hotel.jpg', 'sector-retail.jpg'} else 720)
    return (1672, 941)


def image(page, lang, asset, cls='', eager=False):
    name = IMAGE_MAP[page['slug']]
    width, height = image_dimensions(name)
    alt = t(page['title'], lang) + bi(' — illustrative property scene', ' — 物业场景示意', lang)
    return (f'<img class="{e(cls)}" src="{e(asset(name))}" alt="{e(alt)}" width="{width}" height="{height}" '
            f'loading="{"eager" if eager else "lazy"}" decoding="async"' + (' fetchpriority="high"' if eager else '') + '>')


def render_section(section, lang, index, kind):
    layout = section.get('layout', 'prose')
    if layout not in {'rows', 'split', 'steps', 'table', 'list', 'prose'}:
        raise ValueError('Unknown section layout: ' + layout)
    intro = f'<p class="gc-section-intro">{e(t(section["intro"], lang))}</p>' if section.get('intro') else ''
    paragraphs = ''.join(f'<p>{e(t(p, lang))}</p>' for p in section.get('paragraphs', []))
    items = section.get('items', [])
    if items:
        item_markup = ''.join(
            f'<li class="gc-work-item"><div class="gc-item-heading">'
            + (f'<span class="gc-step-num" aria-hidden="true">{n + 1:02d}</span>' if layout == 'steps' else '')
            + f'<h3>{e(t(item["title"], lang))}</h3></div><p>{e(t(item["text"], lang))}</p></li>'
            for n, item in enumerate(items))
        tag = 'ol' if layout == 'steps' else 'ul'
        paragraphs += f'<{tag} class="gc-work-list">{item_markup}</{tag}>'
    if section.get('table'):
        table = section['table']
        headings = ''.join(f'<th scope="col">{e(t(h, lang))}</th>' for h in table['headers'])
        table_rows = []
        for row in table['rows']:
            cells = []
            for j, cell in enumerate(row):
                tag = 'th scope="row"' if j == 0 else 'td'
                close = 'th' if j == 0 else 'td'
                cells.append('<' + tag + '>' + e(t(cell, lang)) + '</' + close + '>')
            table_rows.append('<tr>' + ''.join(cells) + '</tr>')
        rows = ''.join(table_rows)
        paragraphs += (f'<div class="gc-table-wrap" role="region" tabindex="0" '
                       f'aria-label="{e(t(section["title"], lang))}"><table><thead><tr>{headings}</tr></thead><tbody>{rows}</tbody></table></div>')
    return (f'<section class="gc-section gc-layout-{layout} gc-chapter-{index % 4}" id="{e(section["id"])}" data-gc-chapter>'
            f'<div class="gc-section-heading" data-gc-reveal><p class="gc-kicker">'
            + bi({'service': 'THE WORK', 'sector': 'PROPERTY IN USE', 'article': 'FIELD NOTES'}[kind],
                 {'service': '工作内容', 'sector': '物业运营', 'article': '维护笔记'}[kind], lang)
            + f'</p><h2>{e(t(section["title"], lang))}</h2></div>'
            f'<div class="gc-section-copy" data-gc-reveal>{intro}{paragraphs}</div></section>')


def related_block(page, lang, catalog, link):
    links = []
    for key, kind in [('services', 'service'), ('sectors', 'sector'), ('articles', 'article')]:
        label = {'service': bi('Service', '服务', lang), 'sector': bi('Property type', '商业类型', lang), 'article': bi('Guide', '维护指南', lang)}[kind]
        for slug in page.get('related', {}).get(key, []):
            if slug not in catalog[kind] or slug == page['slug']:
                continue
            item = catalog[kind][slug]
            links.append(f'<a class="gc-related-link" href="{e(link(kind, slug, lang))}"><span class="gc-kicker">{label}</span>'
                         f'<strong>{e(t(item["title"], lang))}</strong><span class="gc-link-arrow" aria-hidden="true">↗</span></a>')
    if not links:
        return ''
    return (f'<section class="gc-related" id="related"><div class="gc-wrap"><div class="gc-related-heading">'
            f'<p class="gc-kicker">{bi("FOLLOW THE WORK", "继续了解", lang)}</p><h2>{bi("Make the connections.", "把相关工作，一起看清。", lang)}</h2></div>'
            f'<div class="gc-related-grid">{"".join(links)}</div></div></section>')


def enquiry_form(page, lang):
    return (f'<section id="enquiry" class="gc-enquiry"><div class="gc-wrap gc-enquiry-grid"><div><p class="gc-kicker">'
            f'{bi("YOUR WORK LIST", "您的工作清单", lang)}</p><h2>{bi("SMALL FIX?<br>BIG PLAN?", "小维修？<br>大项目？", lang)}</h2>'
            f'<p>{bi("Tell us the property, the work and the access window. Save a clear brief to use when arranging the job.", "写下物业、工作事项和进场时间，保存成清楚的需求清单。", lang)}</p></div>'
            f'<form class="gc-brief-form" data-gc-brief novalidate><label>{bi("Property / area", "物业／区域", lang)}'
            f'<input name="property" autocomplete="off"></label><label>{bi("Work required", "需要处理的工作", lang)}'
            f'<textarea name="work" rows="4" required>{e(t(page["title"], lang))}</textarea></label>'
            f'<label>{bi("Access / preferred timing", "进场条件／期望时间", lang)}<input name="access" autocomplete="off"></label>'
            f'<button type="submit" class="gc-button">{bi("Prepare work list", "生成工作清单", lang)} <span aria-hidden="true">↗</span></button>'
            f'<p class="gc-form-status" role="status" aria-live="polite"></p><div class="gc-brief-result" hidden>'
            f'<label>{bi("Your enquiry draft", "您的询价草稿", lang)}<textarea name="draft" rows="7" readonly></textarea></label>'
            f'<div class="gc-brief-actions"><button type="button" data-gc-copy>{bi("Copy text", "复制文本", lang)}</button>'
            f'<button type="button" data-gc-download>{bi("Save TXT", "保存 TXT", lang)}</button></div></div>'
            f'<p class="gc-form-note">{bi("This preview prepares a local draft. It does not send an enquiry.", "此预览生成本地草稿，不会发送询价。", lang)}</p></form></div></section>')


def render_detail(page, lang, catalog, sources, link=None, asset=None, contact_href=None, preview=False):
    """Return scoped body HTML. Supply host link/asset callbacks; append the existing CTA/footer outside."""
    if lang not in {'en', 'zh'}:
        raise ValueError('Supported locales: en, zh')
    link = link or production_link
    asset = asset or (lambda name: '/assets/' + name)
    contact_href = contact_href or ('/zh/contact/' if lang == 'zh' else '/contact/')
    kind = page['kind']
    title, deck = e(t(page['title'], lang)), e(t(page['deck'], lang))
    category = {'service': bi('COMMERCIAL SERVICES', '商业维护服务', lang),
                'sector': bi('PROPERTY TYPES', '商业物业类型', lang),
                'article': bi('THE COASTAL JOURNAL', '海岸维护杂志', lang)}[kind]
    kicker = e(t(page['kicker'], lang))
    action = bi('Plan this work', '安排这项工作', lang)
    hero_photo = image(page, lang, asset, 'gc-hero-image', True)
    photo_note = bi('Illustrative coastal / property imagery', '海岸与物业场景示意', lang)
    if kind == 'service':
        hero = (f'<header class="gc-hero gc-service-hero"><div class="gc-wrap gc-service-hero-grid"><div class="gc-hero-copy">'
                f'<p class="gc-kicker">GOLD COAST / {category}</p><h1>{title}</h1><p class="gc-deck">{deck}</p>'
                f'<div class="gc-hero-actions"><a class="gc-button" href="{e(contact_href)}">{action} <span aria-hidden="true">↗</span></a>'
                f'<a class="gc-text-link" href="#work">{bi("Explore the scope", "查看工作内容", lang)} ↓</a></div></div>'
                f'<figure class="gc-service-photo">{hero_photo}<figcaption>{photo_note}</figcaption>'
                f'<div class="gc-photo-stamp" aria-hidden="true">COASTAL<br>CARE<span>✺</span></div></figure></div>'
                f'<div class="gc-hero-foot"><span>{kicker}</span><span>{bi("ONE-OFF REPAIRS / COORDINATED WORK", "单项维修 / 协同维护", lang)}</span></div></header>')
    elif kind == 'sector':
        hero = (f'<header class="gc-hero gc-sector-hero"><div class="gc-sector-image">{hero_photo}</div><div class="gc-wrap gc-sector-hero-copy">'
                f'<p class="gc-kicker">GOLD COAST / {category}</p><h1>{title}</h1><div class="gc-sector-intro"><p class="gc-deck">{deck}</p>'
                f'<a class="gc-button" href="{e(contact_href)}">{action} <span aria-hidden="true">↗</span></a></div></div>'
                f'<div class="gc-sector-caption"><span>{kicker}</span><small>{photo_note}</small></div></header>')
    else:
        hero = (f'<header class="gc-hero gc-article-hero"><div class="gc-wrap"><div class="gc-journal-line"><p class="gc-kicker">{category}</p>'
                f'<span>{bi("PROPERTY / PEOPLE / THE COAST", "建筑 / 日常 / 海岸", lang)}</span></div><h1>{title}</h1>'
                f'<div class="gc-article-deck"><p>{deck}</p><span class="gc-journal-seal" aria-hidden="true">ELLIS<br>FIELD<br>NOTES</span></div>'
                f'<figure class="gc-article-cover">{hero_photo}<figcaption>{photo_note}</figcaption></figure></div></header>')
    toc_links = ''.join(f'<a href="#{e(s["id"])}" data-gc-toc>{e(t(s["title"],lang))}</a>' for s in page['sections'])
    toc = (f'<nav class="gc-topic-nav" aria-label="{bi("On this page", "本页目录", lang)}"><div class="gc-read-progress" aria-hidden="true"></div>'
           f'<span class="gc-toc-label">{bi("IN THIS GUIDE", "本页内容", lang)}</span><button type="button" class="gc-toc-arrow" data-gc-toc-prev aria-label="{bi("Previous headings", "前面的章节", lang)}">←</button>'
           f'<div class="gc-toc-track">{toc_links}</div><button type="button" class="gc-toc-arrow" data-gc-toc-next aria-label="{bi("Next headings", "后面的章节", lang)}">→</button></nav>')
    lead = (f'<section class="gc-lead gc-wrap" id="work"><p class="gc-kicker">{bi("THE BRIEF", "先把工作说清", lang)}</p>'
            f'<p>{e(t(page["lead"],lang))}</p><span class="gc-lead-sun" aria-hidden="true">✺</span></section>')
    blocks = []
    for i, section in enumerate(page['sections']):
        blocks.append(render_section(section, lang, i, kind))
        if i == 1 and kind != 'article':
            mood_name = {'building-maintenance':'sector-retail.jpg','hotels-resorts':'coastal-maintenance-editorial.png','roofing-waterproofing':'coastal-maintenance-editorial.png','fire-security-access':'sector-hotel.jpg','restaurants-cafes':'coastal-maintenance-editorial.png','landscaping-irrigation':'sector-hospitality.jpg','fit-outs-make-good':'sector-office.jpg'}.get(page['slug'],'coastal-roof-editorial.png' if 'industrial' in page['slug'] or 'warehouse' in page['slug'] else 'sector-hotel.jpg')
            if mood_name == IMAGE_MAP[page['slug']]:
                mood_name = 'coastal-maintenance-editorial.png'
            width, height = image_dimensions(mood_name)
            blocks.append(f'<figure class="gc-photo-break" data-gc-reveal><img src="{e(asset(mood_name))}" width="{width}" height="{height}" loading="lazy" decoding="async" alt="{photo_note}">'
                          f'<figcaption><span>{bi("CARE FOR THE PLACE.<br>PLAN FOR THE PEOPLE.", "维护好场地，<br>安排好日常。", lang)}</span><small>{photo_note}</small></figcaption></figure>')
    faq = ''.join(f'<details class="gc-faq-item"><summary>{e(t(q["q"],lang))}<span aria-hidden="true">+</span></summary><div><p>{e(t(q["a"],lang))}</p></div></details>' for q in page.get('faqs', []))
    faq_block = (f'<section class="gc-faq gc-wrap" id="questions"><div><p class="gc-kicker">{bi("A FEW GOOD QUESTIONS", "常见问题", lang)}</p>'
                 f'<h2>{bi("Good to know.", "把细节问清。", lang)}</h2></div><div>{faq}</div></section>') if faq else ''
    source_links = []
    for sid in page.get('sourceIds', []):
        if sid in sources:
            source = sources[sid]
            label = t(source['label'], lang) if 'label' in source else f'{source["publisher"]} — {source["title"]}'
            source_links.append(f'<li><a href="{e(source["url"])}" target="_blank" rel="noopener noreferrer">{e(label)}</a></li>')
    source_block = (f'<aside class="gc-sources gc-wrap"><h2>{bi("Technical reading", "技术参考", lang)}</h2><ul>{"".join(source_links)}</ul></aside>') if source_links else ''
    body = (hero + toc + lead + f'<div class="gc-chapters gc-wrap">{"".join(blocks)}</div>' + faq_block
            + source_block + related_block(page,lang,catalog,link))
    if kind == 'article' and not preview:
        body += f'<div class="gc-wrap gc-article-next"><a class="gc-button" href="{e(contact_href)}">{action} <span aria-hidden="true">↗</span></a></div>'
    if preview:
        body += enquiry_form(page,lang)
    return f'<article class="gc-v4 gc-v4--{kind}" data-gc-v4 data-gc-lang="{lang}">{body}</article>'
