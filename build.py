from argparse import ArgumentParser
from pathlib import Path
from shutil import copy2, copytree
from xml.etree import ElementTree as ET
from html import escape
from hashlib import sha256
import json
from src.inner_pages_v4 import KINDS, load_catalog, render_detail

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
OUT = DIST
INNER_STYLE = 'gc-inner-v4.css'
INNER_SCRIPT = 'gc-inner-v4.js'
INNER_VERSIONS = {name: sha256((DIST / name).read_bytes()).hexdigest()[:10] for name in (INNER_STYLE, INNER_SCRIPT, 'app.js')}
DATA = json.loads((ROOT / 'src/content.json').read_text(encoding="utf-8"))
PREVIEW_ORIGIN = 'https://goldcoastcommercialrepairscomau.vercel.app'
PRODUCTION_ORIGIN = 'https://goldcoastcommercialrepairs.com.au'
ORIGIN = PREVIEW_ORIGIN
PRODUCTION = False
CANONICAL_URLS = []

def e(x): return escape(str(x), quote=True)
def tr(en, zh, lang): return en if lang == 'en' else zh
def val(item, key, lang): return item[key][lang]
def url(path, lang): return ('/zh' if lang == 'zh' else '') + ('/' if path == '/' else path)
def img(name, alt, cls='', eager=False):
    return f'<img src="/assets/{name}" alt="{e(alt)}" class="{cls}" loading="{"eager" if eager else "lazy"}" decoding="async"'+(' fetchpriority="high"' if eager else '')+'>'
def a(path, text, lang, cls=''):
    return f'<a href="{url(path,lang)}" class="{cls}">{text}</a>'
def button_link(path, text, lang, secondary=False):
    return a(path,e(text),lang,'button'+(' button-outline' if secondary else '')).replace('<a ', '<a data-magnetic ', 1)

NAV = [('/', 'Home', '首页'),('/services/','Services','服务内容'),('/sectors/','Property types','商业类型'),('/news/','News','新闻'),('/faq/','FAQ','FAQ'),('/about/','About us','关于我们'),('/contact/','Contact','联系我们')]
SERVICE_GROUPS = {
    'building-maintenance':'buildings','roofing-waterproofing':'buildings',
    'electrical-lighting':'systems','plumbing-drainage-gas':'systems','hvac-building-systems':'systems','fire-security-access':'systems',
    'landscaping-irrigation':'outdoors','signage-wayfinding':'outdoors','facade-high-access-cleaning':'outdoors','cleaning-waste-hygiene':'outdoors','car-parks-external-works':'outdoors','fit-outs-make-good':'buildings'
}
INNER_CATALOG = load_catalog(ROOT / 'src/content.json')


def wordmark(lang):
    return f'''<a href="{url('/',lang)}" class="wordmark" aria-label="Ellis Gold Coast home"><span class="brand-sun" aria-hidden="true"></span><span><strong>ELLIS<span class="brand-dot">.</span></strong><small>GOLD COAST</small></span></a>'''


def header(path, lang):
    nav=''.join(f'<a href="{url(p,lang)}"'+(' aria-current="page"' if p==path or p!='/' and path.startswith(p) else '')+f'>{tr(en,zh,lang)}</a>' for p,en,zh in NAV)
    other = 'zh' if lang == 'en' else 'en'
    return f'''<a class="skip-link" href="#main">{tr('Skip to content','跳到正文',lang)}</a>
    <div class="topline"><span>{tr('GOLD COAST · QUEENSLAND','GOLD COAST · 黄金海岸',lang)}</span><span>{tr('Buildings. Systems. Outdoor spaces.','建筑 · 设备 · 室外空间',lang)}</span></div>
    <header class="site-header">{wordmark(lang)}
    <button class="menu-toggle" aria-expanded="false" aria-controls="primary-nav">{tr('Menu','菜单',lang)}</button>
    <nav id="primary-nav" aria-label="{tr('Main navigation','主导航',lang)}">{nav}</nav>
    <a href="{url(path,other)}" class="lang-switch" lang="{tr('zh-CN','en-AU',lang)}" aria-label="{tr('切换中文','Switch to English',lang)}">中/EN</a></header>'''

def footer(lang):
    from src.footer_v3 import render_footer
    return render_footer(lang, tr, url, NAV)

def page(path, lang, title, desc, body, cls='', *, inner=False, share_image='coast-hero.webp'):
    relpath=('zh/' if lang=='zh' else '')+(path.strip('/')+'/' if path!='/' else '')
    dest=OUT/relpath/'index.html'
    dest.parent.mkdir(parents=True,exist_ok=True)
    canonical=ORIGIN+url(path,lang)
    CANONICAL_URLS.append(canonical)
    robots_meta = '' if PRODUCTION else '<meta name="robots" content="noindex,nofollow">'
    default_alternate = f'<link rel="alternate" hreflang="x-default" href="{ORIGIN+url(path,"en")}">' if PRODUCTION else ''
    inner_css = f'<link rel="stylesheet" href="/{INNER_STYLE}?v={INNER_VERSIONS[INNER_STYLE]}">' if inner else ''
    inner_js = f'<script defer src="/{INNER_SCRIPT}?v={INNER_VERSIONS[INNER_SCRIPT]}"></script>' if inner else ''
    doc=f'''<!doctype html><html lang="{tr('en-AU','zh-CN',lang)}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#FF642D"><title>{e(title)} | Ellis Gold Coast</title><meta name="description" content="{e(desc)}">{robots_meta}<link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="en-AU" href="{ORIGIN+url(path,'en')}"><link rel="alternate" hreflang="zh-CN" href="{ORIGIN+url(path,'zh')}">{default_alternate}<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:image" content="{ORIGIN}/assets/{e(share_image)}"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/surf-font.css"><link rel="stylesheet" href="/chinese-font.css"><link rel="stylesheet" href="/maximal.css"><link rel="stylesheet" href="/interiors.css">{inner_css}<link rel="stylesheet" href="/footer.css"><script defer src="/app.js?v={INNER_VERSIONS['app.js']}"></script><script defer src="/motion.js"></script>{inner_js}</head><body class="{cls} maximal"><div class="scroll-progress" aria-hidden="true"></div><div class="cursor-orb" aria-hidden="true"></div>{header(path,lang)}<main id="main">{body}</main>{footer(lang)}</body></html>'''
    dest.write_text(doc, encoding="utf-8", newline="\n")

def section_heading(kicker, title, text='', link=None, lang='en'):
    return f'<div class="section-heading" data-reveal><div><p class="eyebrow">{kicker}</p><h2>{title}</h2></div><div class="section-intro">'+(f'<p>{text}</p>' if text else '')+(a(link[0],link[1],lang,'text-link') if link else '')+'</div></div>'

def cta(lang):
    from src.footer_v3 import render_cta
    return render_cta(lang, tr, url)

def faq_items(items, lang):
    entries = []
    for item in items:
        anchor = f' id="{e(item["id"])}"' if item.get('id') else ''
        category = e(item.get('category', 'planning'))
        target = item.get('link')
        guidance = f'<p>{a(target[0], target[1][lang], lang, "text-link")}</p>' if target else ''
        entries.append(
            f'<details{anchor} data-faq data-filter-item data-tags="{category}">'
            f'<summary>{e(val(item,"q",lang))}<span aria-hidden="true">+</span></summary>'
            f'<div class="faq-answer"><p>{e(val(item,"a",lang))}</p>{guidance}</div></details>'
        )
    return ''.join(entries)

def service_row(x, lang, i=0):
    return f'''<a href="{url('/services/'+x['slug']+'/',lang)}" class="service-row" data-filter-item data-tags="{SERVICE_GROUPS[x['slug']]}"><span class="service-mark mark-{i%4}" aria-hidden="true"></span><div><h3>{e(val(x,'title',lang))}</h3><p>{e(val(x,'short',lang))}</p></div><span class="row-view">{tr('Explore','查看',lang)}</span></a>'''

def sector_card(x,lang,i,full=False):
    return f'''<a href="{url('/sectors/'+x['slug']+'/',lang)}" class="sector-card color-{i%4}{' sector-full' if full else ''}" data-tilt data-filter-item data-tags="{e(x['slug'])}"><div class="sector-photo">{img(x['image'],val(x,'title',lang)+' — '+tr('property scene','物业场景配图',lang))}</div><div class="sector-caption"><span class="eyebrow">{tr('PROPERTY CARE','商业物业维护',lang)}</span><h3>{e(val(x,'title',lang))}</h3><p>{e(val(x,'short',lang))}</p><span class="text-link">{tr('Explore this property type','查看对应维护内容',lang)}</span></div></a>'''

def article_card(x,lang,i):
    pic=x['editorial']['cover']
    return f'''<article class="news-card" data-tilt data-filter-item data-tags="{e(x['tag'])}"><a href="{url('/news/'+x['slug']+'/',lang)}"><div class="news-photo">{img(pic,val(x,'title',lang)+' — '+tr('site photograph','场景配图',lang))}<span class="tag">{e(val(x,'category',lang))}</span></div><div class="news-copy"><h3>{e(val(x,'title',lang))}</h3><p>{e(val(x,'summary',lang))}</p><span class="text-link">{tr('Read the story','阅读全文',lang)}</span></div></a></article>'''

def process(lang):
    steps=[('Tell us what needs attention','说明维护事项','Send the property type, location, issue and useful photos.','提供物业类型、位置、问题描述及现场照片。'),('Agree the scope','确认范围与报价','We confirm the work, materials, access and quotation.','我们核对处理范围、材料、进场条件与报价。'),('Coordinate the visit','协调进场施工','We arrange the work around agreed operating and access times.','我们按确认的营业安排与通行时段组织施工。'),('Close out the work','核对完工交付','We record completed work and any items requiring follow-up.','我们整理完工记录，并说明需要后续跟进的项目。')]
    return '<ol class="process-list">'+''.join(f'<li data-reveal><span class="step-num">{i+1:02d}</span><h3>{tr(s[0],s[1],lang)}</h3><p>{tr(s[2],s[3],lang)}</p></li>' for i,s in enumerate(steps))+'</ol>'

def home(lang):
    from src.home_v2 import render
    body=render(lang, DATA, tr, e, val, url, img, a, button_link, service_row, sector_card, article_card, faq_items, process, cta)
    page('/',lang,tr('Gold Coast commercial property maintenance','黄金海岸商业物业维修与维护',lang),tr('Commercial repairs and maintenance for Gold Coast hotels, venues, workplaces and shared spaces.','黄金海岸酒店、餐饮、办公与公共区域的商业物业维修和维护。',lang),body,'page-home')


def page_intro(kicker,title,desc,lang,tone='aqua',image=None):
    return f'<section class="page-intro intro-{tone}"><div class="wrap intro-grid"><div><p class="eyebrow">{kicker}</p><h1>{title}</h1><p class="intro-lead">{desc}</p></div>'+('<div class="intro-photo">'+img(image,tr('Commercial property scene','商业物业场景配图',lang),'',True)+'</div>' if image else '<div class="intro-emblem" aria-hidden="true"><span class="sun-disc"></span><span>CARE<br>FOR THE<br>COAST.</span></div>')+'</div></section>'

def services_page(lang):
    buttons=[('all','All services','全部服务'),('buildings','Buildings','建筑'),('systems','Systems','设备系统'),('outdoors','Outdoor spaces','室外与环境')]
    body=page_intro(tr('GOLD COAST / OUR SERVICES','黄金海岸 / 服务内容',lang),tr('Commercial services.<br><em>Coastal care.</em>','商业物业维护。<br><em>每一项，都有安排。</em>',lang),tr('Commercial maintenance services for buildings, essential systems and outdoor spaces. Use Buildings for faults in fittings and finishes, Systems for equipment or services, and Outdoor spaces for work affecting access, surfaces or grounds.','建筑、设备与室外场地的商业维护服务。五金与饰面问题可查建筑类；设备与管线问题可查设备系统；通道、铺装及场地问题可查室外与环境。',lang),lang,'aqua','sector-hospitality.jpg')
    body+=f'<section class="section wrap" data-filter-group><div class="filter-bar" aria-label="{tr("Filter services","筛选服务",lang)}">'+''.join(f'<button data-filter="{k}" aria-pressed="{"true" if k=="all" else "false"}">{tr(en,zh,lang)}</button>' for k,en,zh in buttons)+'</div><div class="service-directory">'+''.join(service_row(x,lang,i) for i,x in enumerate(DATA['services']))+'</div></section>'+cta(lang)
    page('/services/',lang,tr('Commercial maintenance services','商业维护服务内容',lang),tr('Explore twelve categories of building, equipment and external maintenance for Gold Coast commercial properties.','查看黄金海岸商业物业的十二类建筑、设备与室外维护服务。',lang),body)

def inner_link(kind, slug, lang):
    return url(f'/{KINDS[kind]}/{slug}/', lang)


def inner_detail(kind, x, lang):
    slug = x['slug']
    record = INNER_CATALOG[kind][slug]
    contact_path = '/contact/?' + kind.replace('sector', 'property') + '=' + slug
    body = render_detail(
        record, lang, INNER_CATALOG,
        link=inner_link, asset=lambda filename: f'/assets/{filename}',
        contact_href=url(contact_path, lang), preview=False,
    )
    page(inner_link(kind, slug, 'en'), lang, val(record, 'title', lang),
         val(record, 'metaDescription', lang), body, 'gc-v4-route', inner=True, share_image=record['editorial']['cover'])


def service_detail(x, lang):
    inner_detail('service', x, lang)


def sectors_page(lang):
    body=page_intro(tr('GOLD COAST / PROPERTY TYPES','黄金海岸 / 商业类型',lang),tr('Maintenance for<br>places to stay,<br><em>work & unwind.</em>','酒店与商业空间。<br>工作与经营场所。<br><em>按物业类型维护。</em>',lang),tr('A resort runs differently from a warehouse. Choose a property type to see what we need to know about guest turnover, resident access, trading hours or deliveries before arranging work.','酒店和仓库的运营方式不同。按物业类型查看安排工作前需要了解的客房周转、住户通行、营业时段或送货条件。',lang),lang,'coral')
    body+='<section class="section wrap"><div class="sector-directory">'+''.join(sector_card(x,lang,i,True) for i,x in enumerate(DATA['sectors']))+'</div></section>'+cta(lang)
    page('/sectors/',lang,tr('Commercial property types','商业物业类型',lang),tr('Maintenance for hotels, body corporate, hospitality, retail, offices and industrial properties on the Gold Coast.','黄金海岸酒店、公寓共同物业、餐饮零售、办公和工业物业的维护内容。',lang),body)

def sector_detail(x, lang):
    inner_detail('sector', x, lang)


def news_page(lang):
    body=page_intro(tr('GOLD COAST / NEWS & IDEAS','黄金海岸 / 新闻与资讯',lang),tr('Notes from<br><em>the coast.</em>','来自海岸的<br><em>维护笔记。</em>',lang),tr('Read Coastal maintenance for salt exposure, stormwater and water entry. Choose Property planning for room turnover, shared repairs and outdoor dining operations.','海岸环境维护介绍盐分暴露、暴雨排水和渗水；物业施工安排介绍客房周转、共同物业维修与户外餐饮营业。',lang),lang,'yellow','coast-hero.webp')
    body+=f'<section class="section wrap" data-filter-group><div class="filter-bar"><button data-filter="all" aria-pressed="true">{tr("All stories","全部文章",lang)}</button><button data-filter="coastal" aria-pressed="false">{tr("Coastal maintenance","海岸环境维护",lang)}</button><button data-filter="planning" aria-pressed="false">{tr("Property planning","物业施工安排",lang)}</button></div><div class="news-directory">'+''.join(article_card(x,lang,i) for i,x in enumerate(DATA['articles']))+'</div></section>'+cta(lang)
    page('/news/',lang,tr('Commercial property maintenance news','商业物业维护新闻与资讯',lang),tr('Ideas and guidance for Gold Coast commercial property maintenance.','黄金海岸商业物业维护与施工安排资讯。',lang),body)

def article_detail(x, lang):
    inner_detail('article', x, lang)


def faq_page(lang):
    body=page_intro(tr('GOLD COAST / FREQUENTLY ASKED QUESTIONS','黄金海岸 / 常见问题',lang),tr('Good questions.<br><em>Clear answers.</em>','把问题问清楚。<br><em>把安排说明白。</em>',lang),tr('Work scope, property access, scheduling and the details we need to plan your maintenance.','工作范围、物业进场、施工时间，以及安排维护所需的信息。',lang),lang,'aqua')
    body+=f'<section class="section wrap faq-page-content" data-filter-group><div class="faq-tools"><label for="faq-search">{tr("Find an answer","查找问题",lang)}</label><input id="faq-search" type="search" placeholder="{tr("Try access, photos or hours…","搜索进场、照片、营业时间…",lang)}"><div class="filter-bar"><button data-filter="all" aria-pressed="true">{tr("All questions","全部问题",lang)}</button><button data-filter="planning" aria-pressed="false">{tr("Planning","施工安排",lang)}</button><button data-filter="scope" aria-pressed="false">{tr("Work scope","工作范围",lang)}</button><button data-filter="coastal" aria-pressed="false">{tr("Coastal properties","海岸物业",lang)}</button></div><p data-result-count aria-live="polite"></p></div><p data-no-results hidden role="status">{tr("No matching questions. Try another search or choose All questions.","未找到对应问题。修改搜索内容，或选择全部问题。",lang)}</p><div class="faq-list">{faq_items(DATA["faqs"],lang)}</div></section>'+cta(lang)
    page('/faq/',lang,tr('Commercial maintenance FAQ','商业维护常见问题',lang),tr('Answers about maintenance scope, quoting, access and scheduling for Gold Coast commercial properties.','黄金海岸商业物业维修范围、报价、进场与施工安排问答。',lang),body)

def about_page(lang):
    body=page_intro(tr('ELLIS SERVICES GROUP / GOLD COAST','ELLIS SERVICES GROUP / 黄金海岸',lang),tr('Coastal spirit.<br><em>Practical care.</em>','明快的海岸气息。<br><em>具体的物业维护。</em>',lang),tr('We are Ellis Services Group. We coordinate building repairs, essential systems and outdoor maintenance around the people using each property.','我们是 Ellis Services Group，结合场所的实际使用，协调建筑维修、设备系统和室外维护。',lang),lang,'sand','sector-office.jpg')
    body+=f'<section class="section wrap about-story"><div data-reveal><p class="eyebrow">{tr("ONE PROPERTY. ONE CLEAR PLAN.","一处物业，一份清楚的安排。",lang)}</p><h2>{tr("Care for the place.<br>Consider the people.","照顾物业，<br>也衔接现场日常。",lang)}</h2></div><div class="prose" data-reveal><p>{tr("We work with property managers, business owners and site contacts to identify what needs attention and how the work should be organised. A small repair, a planned maintenance visit or a project involving several trades starts with a clear scope.","我们与物业经理、经营者及现场联系人沟通，确认需要处理的事项与施工条件。无论是单次维修、定期维护还是多工种项目，都从明确的工作范围开始。",lang)}</p><p>{tr("We confirm access, materials, work areas and the order of tasks before arranging the visit. At completion, we record the agreed work and identify any further items for the property manager to consider.","进场前，我们确认通行、材料、作业区域与施工顺序。完成后整理已确认范围内的工作记录，并说明需要后续跟进的事项。",lang)}</p></div></section><section class="about-values"><div class="wrap value-grid"><article><span class="eyebrow">{tr("SCOPE","范围",lang)}</span><h2>{tr("Know what’s included.","做什么，先说清楚。",lang)}</h2><p>{tr("A useful quotation explains the work, access assumptions and inclusions.","报价说明工作内容、进场条件与包含项目。",lang)}</p></article><article><span class="eyebrow">{tr("COORDINATION","协调",lang)}</span><h2>{tr("Make the visit count.","进一次场，安排到位。",lang)}</h2><p>{tr("We bring related tasks together and agree their sequence around your property.","关联事项集中梳理，结合物业安排确认施工顺序。",lang)}</p></article><article><span class="eyebrow">{tr("HANDOVER","交付",lang)}</span><h2>{tr("Leave a useful record.","做完，有记录。",lang)}</h2><p>{tr("We record agreed checks and completed work against the original defect numbers. If we discover extra damage, we confirm the change in cost and timing before proceeding.","我们按原缺陷编号记录约定检查和完工内容。若发现额外损伤，先确认费用和时段的变化，再继续。",lang)}</p></article></div></section><section class="section wrap">{section_heading(tr("HOW THE WORK COMES TOGETHER","从需求到完工",lang),tr("From first conversation<br>to a clear handover.","从第一次沟通，<br>到明确的完工交付。",lang),"",None,lang)}{process(lang)}</section>'+cta(lang)
    page('/about/',lang,tr('About Ellis commercial property care','关于 Ellis 商业物业维护',lang),tr('Building, system and outdoor maintenance coordinated around Gold Coast commercial properties.','围绕黄金海岸商业物业，统一安排建筑、设备与室外维护。',lang),body)

def contact_page(lang):
    service_options=''.join(f'<option value="{x["slug"]}">{e(val(x,"title",lang))}</option>' for x in DATA['services'])
    sector_options=''.join(f'<option value="{x["slug"]}">{e(val(x,"title",lang))}</option>' for x in DATA['sectors'])
    articles = ''.join(f'<option value="{e(x["slug"])}">{e(val(x,"title",lang))}</option>' for x in DATA['articles'])
    topic_markup = f'<div class="field-full" data-enquiry-article hidden><label for="article">{tr("Related guide", "相关指南", lang)}</label><select id="article" name="article"><option value="">{tr("No guide selected", "未选择指南", lang)}</option>{articles}</select></div>'
    body=f'''<section class="contact-section wrap"><div class="contact-copy"><p class="eyebrow">{tr('GOLD COAST / LET’S TALK PROPERTY','黄金海岸 / 联系我们',lang)}</p><h1>{tr('Tell us what<br>needs a little<br><em>attention.</em>','说说你的物业，<br>有哪些需要<br><em>处理的问题。</em>',lang)}</h1><p class="intro-lead">{tr('Start with the property, the problem and the timing. We can build the scope from there.','从物业类型、具体问题和期望时间开始，梳理这次需要处理的工作。',lang)}</p><div class="contact-note"><h2>{tr('Useful details to include','可以一起提供的信息',lang)}</h2><ul><li>{tr('Property type and Gold Coast suburb','物业类型与黄金海岸所在区域',lang)}</li><li>{tr('Room, level or defect number, what changed, and when it happens','房号、楼层或缺陷编号，以及具体变化和发生时间',lang)}</li><li>{tr('Access hours, site contact, keys, approvals or any outage limits','可进场时段、现场联系人、钥匙、审批或停用限制',lang)}</li><li>{tr('Keep overview and close-up photos with your records for later discussion','保留现场全景和近照，便于后续沟通',lang)}</li></ul></div><div class="contact-photo">{img('coast-hero.webp',tr('Gold Coast waterfront','海岸场景设计配图',lang))}</div></div>
    <div class="form-panel"><form id="enquiry-form"><p class="eyebrow">{tr('YOUR PROPERTY DETAILS','项目需求',lang)}</p><h2>{tr('Let’s make a plan.','把维护安排起来。',lang)}</h2><div class="form-grid"><div><label for="name">{tr('Your name','姓名',lang)} <span>*</span></label><input id="name" name="name" autocomplete="name" required maxlength="100"></div><div><label for="email">{tr('Email address','邮箱',lang)} <span>*</span></label><input id="email" name="email" type="email" autocomplete="email" required maxlength="200"></div><div><label for="suburb">{tr('Property suburb','物业所在区域',lang)} <span>*</span></label><input id="suburb" name="suburb" autocomplete="address-level2" required maxlength="100" placeholder="{tr('e.g. Broadbeach','例如 Broadbeach',lang)}"></div><div><label for="property">{tr('Property type','物业类型',lang)} <span>*</span></label><select id="property" name="property" required><option value="">{tr('Select a property type','选择物业类型',lang)}</option>{sector_options}</select></div><div class="field-full"><label for="service">{tr('What kind of work?','需要哪类工作？',lang)}</label><select id="service" name="service"><option value="">{tr('Select a service (optional)','选择服务项目（选填）',lang)}</option>{service_options}</select></div>{topic_markup}<div class="field-full"><label for="access-window">{tr('Preferred access window (optional)','期望的进场时段（选填）',lang)}</label><input id="access-window" name="access-window" maxlength="200" placeholder="{tr('e.g. Weekdays before opening','例如工作日营业前',lang)}"></div><div class="field-full"><label for="message">{tr('Tell us about the issue','描述需要处理的问题',lang)} <span>*</span></label><textarea id="message" name="message" required rows="5" maxlength="6000" placeholder="{tr('What needs attention? When can the property be accessed?','具体哪些部位需要处理？什么时间方便进场？',lang)}"></textarea></div></div><button class="button" type="submit">{tr('View work summary','查看需求清单',lang)}</button></form><section id="enquiry-result" hidden tabindex="-1"><p class="eyebrow">{tr('PROPERTY WORK SUMMARY','物业需求清单',lang)}</p><h2>{tr('Your work summary','已整理的维修需求',lang)}</h2><p role="status" data-enquiry-status hidden></p><pre id="enquiry-summary"></pre><div class="button-row"><button type="button" id="download-enquiry" class="button">{tr('Download summary','下载清单',lang)}</button><button type="button" id="copy-enquiry" class="button button-outline">{tr('Copy details','复制内容',lang)}</button><button type="button" id="edit-enquiry" class="text-button">{tr('Edit details','修改需求',lang)}</button></div></section></div></section>'''
    page('/contact/',lang,tr('Contact · Plan commercial maintenance','联系我们 · 安排商业物业维护',lang),tr('Prepare a maintenance enquiry for your Gold Coast commercial property.','整理黄金海岸商业物业维修与维护需求。',lang),body,'page-contact')

def credits(lang):
    sources=json.loads((ROOT/'src/assets-sources.json').read_text(encoding="utf-8")) if (ROOT/'src/assets-sources.json').exists() else {}
    body=page_intro(tr('IMAGE CREDITS','图片说明',lang),tr('Scenes of<br><em>coastal life.</em>','关于这些<br><em>海岸场景。</em>',lang),tr('Photography and image credits for this website.','本站摄影与图像来源。',lang),lang,'sand')
    additional_credits = ' · '.join(
        e(photo.get("photographer", photo.get("title", "Pexels")))
        for photo in sources if photo.get('provider') == 'Pexels'
    )
    body+='<section class="section wrap prose"><h2>'+tr('Coastal hero image','首页海岸主视觉',lang)+'</h2><p>'+tr('The Gold Coast hero uses generated imagery.','首页海岸主图为生成图像。',lang)+'</p><h2>'+tr('Property photography','物业场景摄影',lang)+'</h2><p>Nico Smit · Johan Mouchet · ANNIE HATUANH · Alesia Kazantceva · Mathias Reding / Unsplash</p><p>'+additional_credits+' / Pexels</p><p>'+tr('Property photography includes stock images and generated editorial scenes of a resort, a maintenance setting and a roof. ','物业图片来源包括图库摄影以及生成的度假、维修和屋面图像。',lang)+'</p></section>'
    page('/image-credits/',lang,tr('Image credits','图片说明',lang),tr('Image sources and design imagery.','海岸设计图片、图库摄影与来源说明。',lang),body)

def write_crawl_files():
    robots = OUT / 'robots.txt'
    sitemap = OUT / 'sitemap.xml'
    if PRODUCTION:
        urlset = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
        for canonical in sorted(CANONICAL_URLS):
            ET.SubElement(ET.SubElement(urlset, 'url'), 'loc').text = canonical
        ET.indent(urlset)
        ET.ElementTree(urlset).write(sitemap, encoding='utf-8', xml_declaration=True)
        rules = f'User-agent: *\nDisallow:\nSitemap: {ORIGIN}/sitemap.xml\n'
    else:
        sitemap.unlink(missing_ok=True)
        rules = 'User-agent: *\nDisallow: /\n'
    robots.write_text(rules, encoding='utf-8', newline='\n')


def build():
    for lang in ['en','zh']:
        home(lang); services_page(lang); sectors_page(lang); news_page(lang); faq_page(lang); about_page(lang); contact_page(lang); credits(lang)
        for x in DATA['services']: service_detail(x,lang)
        for x in DATA['sectors']: sector_detail(x,lang)
        for x in DATA['articles']: article_detail(x,lang)

    (OUT/'404.html').write_text('''<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Page not found | Ellis Gold Coast</title><meta name="description" content="This page is not available. Return to Ellis Gold Coast commercial property maintenance."><meta name="robots" content="noindex"><meta name="theme-color" content="#FF642D"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/surf-font.css"><link rel="stylesheet" href="/chinese-font.css"><link rel="stylesheet" href="/maximal.css"><style>body.page-not-found{min-height:100svh;display:grid;place-items:center;padding:35px 22px;background:var(--gc-orange)}body.page-not-found .not-found{width:min(900px,100%);margin:0;padding:clamp(30px,7vw,90px);background:var(--gc-sun);border:3px solid var(--gc-ink);box-shadow:12px 12px 0 var(--gc-ink);text-align:left}body.page-not-found .error-code{display:inline-block;background:var(--gc-pink);border:2px solid var(--gc-ink);padding:7px 20px;font-family:var(--gc-display);font-size:2rem;transform:rotate(-4deg);margin-bottom:28px}body.page-not-found h1{font-size:clamp(2.3rem,8vw,5.6rem);line-height:1.06;overflow-wrap:break-word}body.page-not-found .error-actions{display:flex;align-items:center;flex-wrap:wrap;gap:22px;margin-top:30px}body.page-not-found .button{background:var(--gc-aqua);color:var(--gc-ink)}body.page-not-found .button:hover{background:var(--gc-pink)}</style></head><body class="maximal page-not-found"><main id="main" class="not-found"><p class="eyebrow">ELLIS / GOLD COAST</p><span class="error-code" aria-label="Error 404">404</span><h1>This path<br>ends here.</h1><p>The page you are looking for is not available.</p><div class="error-actions"><a class="button" href="/">Back to home</a><a class="text-link" href="/zh/" lang="zh-CN">返回中文首页</a></div></main></body></html>''', encoding="utf-8", newline="\n")
    write_crawl_files()
    (OUT/'assets/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="18" fill="#FFE34D"/><circle cx="32" cy="32" r="15" fill="#241611"/><path d="M32 7v5M32 52v5M7 32h5M52 32h5M14 14l4 4M46 46l4 4M14 50l4-4M46 18l4-4" stroke="#241611" stroke-width="4"/></svg>', encoding="utf-8", newline="\n")
    print(json.dumps({'html_pages':len(list(OUT.rglob('*.html'))),'services':len(DATA['services']),'sectors':len(DATA['sectors']),'articles':len(DATA['articles'])}))


if __name__ == '__main__':
    parser = ArgumentParser(description='Build the Gold Coast static site')
    parser.add_argument('--production-dir', type=Path, metavar='DIRECTORY',
                        help='Write indexable output to a new directory outside dist')
    args = parser.parse_args()
    if args.production_dir is not None:
        OUT = args.production_dir.resolve()
        if OUT.exists() or OUT.is_relative_to(DIST):
            parser.error('--production-dir must be a new directory outside dist')
        OUT.mkdir(parents=True)
        copytree(DIST / 'assets', OUT / 'assets')
        for pattern in ('*.css', '*.js'):
            for asset in DIST.glob(pattern):
                copy2(asset, OUT / asset.name)
        ORIGIN = PRODUCTION_ORIGIN
        PRODUCTION = True
    build()
