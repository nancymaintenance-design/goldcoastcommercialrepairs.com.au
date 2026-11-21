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


def production_link(kind, slug, lang):
    return ('/zh' if lang == 'zh' else '') + '/' + KINDS[kind] + '/' + slug + '/'


ASSET_DIMENSIONS = {
    row['filename']: tuple(row['dimensions'])
    for row in json.loads(Path(__file__).with_name('assets-sources.json').read_text(encoding='utf-8'))
    if row.get('dimensions')
}


def image_dimensions(name):
    if name in ASSET_DIMENSIONS:
        return ASSET_DIMENSIONS[name]
    if name.startswith('sector-'):
        return (1080, 608 if name in {'sector-hotel.jpg', 'sector-retail.jpg'} else 720)
    return (1672, 941)


def render_section(section, lang, contextual_links="", media="", context="", *, heading="h2"):
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
    return (
        f'<section class="gc-section gc-layout-{layout}" id="{e(section["id"])}" data-gc-chapter>'
        f'<div class="gc-section-heading" data-gc-reveal><{heading}>{e(t(section["title"],lang))}</{heading}>{context}</div>{media}'
        f'<div class="gc-section-copy" data-gc-reveal>{intro}{paragraphs}{contextual_links}</div></section>'
    )


def related_block(page, lang, catalog, link, asset):
    links = []
    promoted = []
    editorial = page['editorial']
    used_images = {editorial['cover'], *(photo['file'] for photo in editorial['features'])}
    used_images.update(editorial[key]['file'] for key in ('fieldPhoto', 'storyPhoto') if key in editorial)
    for key, kind in [('services', 'service'), ('sectors', 'sector'), ('articles', 'article')]:
        label = {'service': bi('Service', '服务', lang), 'sector': bi('Property type', '商业类型', lang), 'article': bi('Guide', '维护指南', lang)}[kind]
        for slug in page.get('related', {}).get(key, []):
            if slug not in catalog[kind] or slug == page['slug']:
                continue
            item = catalog[kind][slug]
            href = e(link(kind, slug, lang))
            title = e(t(item['title'], lang))
            if page['kind'] == 'article' and kind == 'article' and len(promoted) < 2:
                candidate = item['editorial']
                options = [candidate['cover'], *(photo['file'] for photo in candidate['features'])]
                filename = next((name for name in options if name not in used_images), None)
            else:
                filename = None
            if filename:
                used_images.add(filename)
                cover = picture(filename, asset, '')
                promoted.append(f'<a class="gc-related-link gc-related-feature" href="{href}">'
                                f'<span aria-hidden="true">{len(promoted)+1:02d}</span>{cover}<strong>{title}</strong>'
                                '<span aria-hidden="true" class="gc-link-arrow">↗</span></a>')
            else:
                links.append(f'<a class="gc-related-link" href="{href}"><span class="gc-kicker">{label}</span>'
                             f'<strong>{title}</strong><span class="gc-link-arrow" aria-hidden="true">↗</span></a>')
    if not (links or promoted):
        return ''
    cards = f'<div class="gc-related-features">{"".join(promoted)}</div>' if promoted else ''
    return (f'<section class="gc-related" id="related"><div class="gc-related-heading">'
            f'<h2>{bi("Continue reading", "继续阅读", lang) if page["kind"] == "article" else bi("Related work", "相关维护内容", lang)}</h2></div>{cards}'
            f'<div class="gc-related-grid">{"".join(links)}</div></section>')


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


def picture(name, asset, alt, *, cls='', eager=False):
    width, height = image_dimensions(name)
    loading = 'eager' if eager else 'lazy'
    priority = ' fetchpriority="high"' if eager else ''
    return (f'<img class="{e(cls)}" src="{e(asset(name))}" alt="{e(alt)}" width="{width}" height="{height}" '
            f'loading="{loading}" decoding="async"{priority}>')


def editorial_links(entries, lang, catalog, link):
    links = []
    for kind, slug in entries:
        record = catalog[kind][slug]
        label = t(record.get('listingTitle', record['title']), lang)
        links.append(f'<a href="{e(link(kind, slug, lang))}">{e(label)} <span aria-hidden="true">↗</span></a>')
    return f'<div class="gc-context-links">{"".join(links)}</div>' if links else ''


def scene_markup(photo, lang, asset, class_name=''):
    caption = t(photo['caption'], lang)
    points = ''.join(
        f'<span class="gc-photo-point" style="--x:{int(point["x"])}%;--y:{int(point["y"])}%;">'
        f'{e(t(point["label"], lang))}</span>'
        for point in photo.get('points', [])
    )
    return (f'<figure class="gc-figure {class_name}" data-gc-reveal data-gc-photo>'
            + picture(photo['file'], asset, caption) + points
            + f'<figcaption>{e(caption)}</figcaption></figure>')


def render_hero(page, lang, asset, contact_href, order):
    kind = page['kind']
    editorial = page['editorial']
    title = t(page['title'], lang)
    labels = {
        'service': ('Services', '服务内容', 'View the scope', '查看维修范围', '#work'),
        'sector': ('Property care', '商业物业维护', 'Prepare a property brief', '整理物业需求', contact_href),
        'article': ('Coast Notes', '海岸维护观察', 'Start reading', '开始阅读', '#work'),
    }
    en, zh, action_en, action_zh, href = labels[kind]
    if kind == 'sector' and lang == 'zh':
        title += '维护'
    number = f'<span class="gc-index" aria-hidden="true">{order:02d}</span>' if kind == 'service' else ''
    cue = f'<span class="gc-hero-note">{e(t(editorial['strap'], lang))}</span>' if kind == 'service' else ''
    lines = editorial.get('titleLinesZh') if lang == 'zh' else None
    if kind == 'service':
        category = f'<strong>{bi(en, zh, lang)}</strong> / {e(t(page["title"], "en"))}'
    elif kind == 'article':
        category = f'<strong>{en}</strong> / {zh if lang == "zh" else "GOLD COAST"}'
    else:
        category = f'<strong>{e(t(page["title"], "en"))}</strong> / GOLD COAST'
    punctuation = '<span class="gc-dot" aria-hidden="true">。</span>' if lang == 'zh' else '<span class="gc-dot" aria-hidden="true">.</span>'
    if lines:
        title_markup = '<wbr>'.join(
            f'<span class="gc-title-line">{e(line)}{punctuation if i == len(lines) - 1 else ""}</span>'
            for i, line in enumerate(lines)
        )
    else:
        title_markup = e(title) + punctuation
    return (
        '<header class="gc-hero"><div class="gc-hero-visual" data-gc-photo>'
        + picture(editorial['cover'], asset, t(editorial['coverAlt'], lang), cls='gc-hero-image', eager=True)
        + f'{number}{cue}</div>'
          f'<div class="gc-wrap gc-hero-copy"><p class="gc-kicker">{category}</p><h1>{title_markup}</h1>'
          f'<p class="gc-deck">{e(t(page["deck"], lang))}</p><div class="gc-hero-actions">'
          f'<a class="gc-button" href="{e(href)}">{bi(action_en, action_zh, lang)} '
          f'<span aria-hidden="true">{("↓" if kind == "article" else "↗")}</span></a></div></div></header>'
    )


def render_toc(sections, editorial, kind, lang):
    labels = editorial.get('nav', {})
    links = ''.join(
        f'<a href="#{e(section["id"])}" data-gc-toc>{e(t(labels.get(section["id"], section["title"]), lang))}</a>'
        for section in sections
    )
    label = bi('In this article', '本文导览', lang) if kind == 'article' else bi('On this page', '本页目录', lang)
    return (f'<nav class="gc-topic-nav" aria-label="{label}"><div class="gc-read-progress" aria-hidden="true"></div>'
            f'<div class="gc-toc-inner"><span class="gc-toc-label">{label}</span>'
            f'<button type="button" class="gc-toc-arrow" data-gc-toc-prev aria-label="{bi("Previous headings", "前面的章节", lang)}">←</button>'
            f'<div class="gc-toc-track">{links}</div>'
            f'<button type="button" class="gc-toc-arrow" data-gc-toc-next aria-label="{bi("Next headings", "后面的章节", lang)}">→</button></div></nav>')


def feature_chapter(section, photo, num, lang, asset, catalog, link, *, secondary=False, lead_media=False):
    label = t(photo['caption'], lang)
    links = editorial_links(photo.get('links', []), lang, catalog, link)
    number = f'<div class="gc-chapter-index"><span aria-hidden="true">{num:02d} / </span>{e(label)}</div>'
    media = scene_markup(photo, lang, asset)
    if photo.get('companion'):
        media = f'<div class="gc-feature-pair">{media}{scene_markup(photo["companion"], lang, asset)}</div>'
    if lead_media:
        return f'<div class="gc-feature gc-feature--lead">{number}{render_section(section, lang, links, media)}</div>'
    style = ' gc-feature--secondary' if secondary else ''

    return f'<div class="gc-feature{style}">{number}{media}{render_section(section, lang, links)}</div>'


def compare_chapter(section, editorial, lang, catalog, link, methods=""):
    links = editorial_links(editorial.get('compareLinks', []), lang, catalog, link)
    rows = []
    for row in editorial.get('workflow', []):
        steps = ''.join(f'<li>{e(t(step, lang))}</li>' for step in row['steps'])
        rows.append(f'<div class="gc-flow-row"><dt>{e(t(row["area"], lang))}</dt><dd><ol>{steps}</ol></dd></div>')
    workflow = f'<dl class="gc-workflow">{"".join(rows)}</dl>' if rows else ''
    return f'<div class="gc-compare"><div class="gc-wrap">{render_section(section, lang, links)}{methods}{workflow}</div></div>'


def render_delivery(page, lang, asset, contact_href, closing_chapter='', brief=''):
    editorial = page['editorial']
    handover = editorial['handover']
    photo = editorial.get('deliveryPhoto')
    title = t(handover['title'], lang)
    note = t(handover['note'], lang)
    checklist = ''.join(f'<li>{e(t(item, lang))}</li>' for item in handover['checklist'])
    action = bi('Prepare an enquiry', '整理维修需求', lang)
    media = scene_markup(photo, lang, asset, 'gc-delivery-image') if photo else ''
    prep = f'<div class="gc-delivery-prep">{media}{brief}</div>' if media or brief else ''
    article = page['kind'] == 'article'
    inline_chapter = '' if article else closing_chapter
    return (f'<div class="gc-delivery"><div class="gc-wrap gc-delivery-inner">{prep}'
            f'<div class="gc-delivery-copy">{closing_chapter if article else ""}<section id="next-step">'
            f'<h2>{e(title)}</h2><p>{e(note)}</p>{inline_chapter}<ul class="gc-delivery-checks">{checklist}</ul>'
            f'<a class="gc-button" href="{e(contact_href)}">{action} <span aria-hidden="true">↗</span></a>'
            '</section></div></div></div>')


def render_faq(page, lang):
    faq = ''.join(
        f'<details class="gc-faq-item"><summary>{e(t(q["q"], lang))}<span aria-hidden="true">+</span></summary>'
        f'<div><p>{e(t(q["a"], lang))}</p></div></details>'
        for q in page.get('faqs', [])
    )
    return f'<section class="gc-faq" id="questions"><h2>{bi("Common questions", "常见问题", lang)}</h2>{faq}</section>' if faq else ''


def render_detail(page, lang, catalog, link=None, asset=None, contact_href=None, preview=False):
    """Render the service, property or journal detail within the shared site shell."""
    if lang not in {'en', 'zh'}:
        raise ValueError('Supported locales: en, zh')
    link = link or production_link
    asset = asset or (lambda name: '/assets/' + name)
    contact_href = contact_href or ('/zh/contact/' if lang == 'zh' else '/contact/')
    kind = page['kind']
    editorial = page['editorial']
    sections = page['sections']
    comparisons = [section for section in sections if section.get('table')]
    prose = [section for section in sections if not section.get('table')]
    photos = editorial['features']
    photo_count = 1 if kind == 'article' else len(photos)
    remaining = prose[photo_count:]
    closing = ''
    brief = ''
    order = list(catalog[kind]).index(page['slug']) + 1
    hero = render_hero(page, lang, asset, contact_href, order)
    lead = f'<div class="gc-lead-copy"><h2>{e(t(editorial["leadTitle"], lang))}</h2><p>{e(t(page["lead"], lang))}</p></div>'
    scenario = f'<p class="gc-scenario">{e(t(editorial["workingExample"], lang))}</p>'

    if kind == 'article':
        article_order = prose[:2] + comparisons + prose[2:]
        toc = render_toc(article_order, editorial, kind, lang)
        intro = render_section(prose[0], lang, editorial_links(photos[0].get('links', []), lang, catalog, link))
        field_photo = editorial.get('fieldPhoto')
        note = f'<aside class="gc-field-note">{scene_markup(field_photo, lang, asset)}</aside>' if field_photo else ''
        gallery = ''.join(scene_markup(photo, lang, asset) for photo in photos if photo['file'] != (field_photo or {}).get('file'))
        takeaway = t(editorial['takeaway'], lang)
        second = (f'<div class="gc-article-spread"><span aria-hidden="true" class="gc-spread-number">02</span>'
                  f'{render_section(prose[1], lang)}<aside class="gc-takeaway"><p>{e(takeaway)}</p></aside></div>')
        comparison = ''.join(compare_chapter(s, editorial, lang, catalog, link) for s in comparisons)
        closing = render_section(remaining[-1], lang)
        story_image = scene_markup(editorial['storyPhoto'], lang, asset)
        story_sections = ''.join(
            render_section(section, lang, context=scenario if i == 0 else '')
            for i, section in enumerate(remaining[1:-1])
        )
        story = f'<div class="gc-story-feature">{story_image}<div>{story_sections}</div></div>'
        main = (f'<div class="gc-wrap gc-article-opening" id="work">{toc}<div>{lead}{intro}</div>{note}</div>'
                f'<div class="gc-wrap gc-article-gallery">{gallery}</div><div class="gc-wrap">{second}</div>'
                f'{comparison}<div class="gc-wrap gc-story">{story}</div>')
    else:
        ordered = prose[:photo_count] + comparisons + remaining
        toc = render_toc(ordered, editorial, kind, lang)
        features = ''.join(
            feature_chapter(section, photo, i + 1, lang, asset, catalog, link, secondary=i % 2 == 1, lead_media=kind == "service" and i == 0)
            for i, (section, photo) in enumerate(zip(prose, photos))
        )
        scene = editorial.get('scene')
        wide = scene_markup(scene, lang, asset, 'gc-wide-scene') if scene else ''
        lead_block = f'<section class="gc-wrap gc-lead" id="work">{lead}</section>'
        if remaining and remaining[-1].get('layout') == 'prose':
            closing = render_section(remaining[-1], lang, heading='h3')
            remaining = remaining[:-1]
        brief = render_section(remaining[-1], lang)
        methods = ''.join(
            render_section(section, lang, context=scenario if i == 0 else '')
            for i, section in enumerate(remaining[:-1])
        )
        comparison = ''.join(
            compare_chapter(section, editorial, lang, catalog, link, f'<div class="gc-method">{methods}</div>')
            for section in comparisons
        )
        main = f'{toc}{lead_block}{wide}<div class="gc-wrap gc-features">{features}</div>{comparison}'

    faq = render_faq(page, lang)
    related = related_block(page, lang, catalog, link, asset)
    delivery = render_delivery(page, lang, asset, contact_href, closing, brief)
    resources = []
    if faq:
        label = bi('Common questions', '常见问题', lang)
        resources.append(f'<details class="gc-resource"><summary>{label}</summary>{faq}</details>')
    if kind == 'article':
        body = hero + main + f'<div class="gc-wrap gc-journal-links">{related}</div>' + delivery
    else:
        if related:
            label = bi('Related work', '相关维护内容', lang)
            resources.append(f'<details class="gc-resource"><summary>{label}</summary>{related}</details>')
        body = hero + main + delivery
    if resources:
        body += f'<div class="gc-wrap gc-resource-strip">{"".join(resources)}</div>'
    if preview:
        body += enquiry_form(page, lang)
    return f'<article class="gc-v4 gc-v4--{kind}" data-gc-v4 data-gc-lang="{lang}">{body}</article>'
