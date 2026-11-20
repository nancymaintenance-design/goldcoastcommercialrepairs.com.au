from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
DATA = json.loads((ROOT / 'src/content.json').read_text(encoding="utf-8"))
ORIGIN = 'https://ellis-gold-coast-coastal.nancy-maintenance.chatgpt.site'

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
SERVICES = {x['slug']:x for x in DATA['services']}

def sector_image(i):
    return ['sector-hotel.jpg','coast-hero.webp','sector-hospitality.jpg','sector-retail.jpg','sector-office.jpg','sector-industrial.jpg','sector-industrial.jpg','sector-office.jpg'][i%8]

def header(path, lang):
    nav=''.join(f'<a href="{url(p,lang)}"'+(' aria-current="page"' if p==path or p!='/' and path.startswith(p) else '')+f'>{tr(en,zh,lang)}</a>' for p,en,zh in NAV)
    other = 'zh' if lang == 'en' else 'en'
    return f'''<a class="skip-link" href="#main">{tr('Skip to content','跳到正文',lang)}</a>
    <div class="topline"><span>{tr('GOLD COAST · QUEENSLAND','GOLD COAST · 黄金海岸',lang)}</span><span>{tr('Buildings. Systems. Outdoor spaces.','建筑 · 设备 · 室外空间',lang)}</span><button class="motion-toggle" data-motion-toggle aria-pressed="false"><span class="motion-dot" aria-hidden="true"></span><span data-motion-state>{tr('MOTION ON','动效开启',lang)}</span></button></div>
    <header class="site-header"><a href="{url('/',lang)}" class="wordmark" aria-label="Ellis Gold Coast home"><span class="brand-sun" aria-hidden="true"></span><span><strong>ELLIS<span class="brand-dot">.</span></strong><small>GOLD COAST</small></span></a>
    <button class="menu-toggle" aria-expanded="false" aria-controls="primary-nav">{tr('Menu','菜单',lang)}</button>
    <nav id="primary-nav" aria-label="{tr('Main navigation','主导航',lang)}">{nav}</nav>
    <a href="{url(path,other)}" class="lang-switch" lang="{tr('zh-CN','en-AU',lang)}" aria-label="{tr('切换中文','Switch to English',lang)}">{tr('中','EN',lang)}</a></header>'''

def footer(lang):
    links=''.join(a(p,tr(en,zh,lang),lang) for p,en,zh in NAV[1:])
    return f'''<footer class="site-footer"><div class="footer-masthead" aria-hidden="true">ELLIS / GC</div><div class="footer-top wrap"><div><a class="wordmark" href="{url('/',lang)}"><span class="brand-sun" aria-hidden="true"></span><span><strong>ELLIS.</strong><small>GOLD COAST</small></span></a><p>{tr('A little coastal spirit.<br>A lot of care for your property.','海岸生活的明快。<br>商业物业的细致维护。',lang)}</p></div><nav aria-label="{tr('Footer navigation','页脚导航',lang)}">{links}</nav><div class="footer-location"><span class="eyebrow">GOLD COAST, QLD</span><p>{tr('Commercial buildings,<br>hospitality & shared spaces.','商业楼宇、酒店餐饮<br>与公共区域。',lang)}</p>{a('/contact/',tr('Plan your next job','安排下一项维护',lang),lang,'text-link')}</div></div>
    <div class="footer-bottom wrap"><span>© 2026 Ellis Services Group</span><span>{tr('Design preview · Enquiries are prepared locally, not sent.','设计预览 · 表单仅生成本地草稿，尚未发送。',lang)}</span>{a('/image-credits/',tr('Image credits','图片说明',lang),lang)}</div></footer>'''

def page(path, lang, title, desc, body, cls=''):
    relpath=('zh/' if lang=='zh' else '')+(path.strip('/')+'/' if path!='/' else '')
    dest=OUT/relpath/'index.html'
    dest.parent.mkdir(parents=True,exist_ok=True)
    canonical=ORIGIN+url(path,lang)
    doc=f'''<!doctype html><html lang="{tr('en-AU','zh-CN',lang)}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#FF642D"><title>{e(title)} | Ellis Gold Coast</title><meta name="description" content="{e(desc)}"><meta name="robots" content="noindex,nofollow"><link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="en-AU" href="{ORIGIN+url(path,'en')}"><link rel="alternate" hreflang="zh-CN" href="{ORIGIN+url(path,'zh')}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:image" content="{ORIGIN}/assets/coast-hero.webp"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/surf-font.css"><link rel="stylesheet" href="/chinese-font.css"><link rel="stylesheet" href="/maximal.css"><link rel="stylesheet" href="/interiors.css"><script defer src="/app.js"></script><script defer src="/motion.js"></script></head><body class="{cls} maximal"><div class="scroll-progress" aria-hidden="true"></div><div class="cursor-orb" aria-hidden="true"></div>{header(path,lang)}<main id="main">{body}</main>{footer(lang)}</body></html>'''
    dest.write_text(doc, encoding="utf-8", newline="\n")

def section_heading(kicker, title, text='', link=None, lang='en'):
    return f'<div class="section-heading" data-reveal><div><p class="eyebrow">{kicker}</p><h2>{title}</h2></div><div class="section-intro">'+(f'<p>{text}</p>' if text else '')+(a(link[0],link[1],lang,'text-link') if link else '')+'</div></div>'

def cta(lang):
    return f'''<section class="closing wrap" data-reveal><div class="closing-copy"><p class="eyebrow">{tr('LET’S MAKE A PLAN','从下一项维护开始',lang)}</p><h2>{tr('LET’S GET<br>TO WORK.','一起把维护<br>安排起来。',lang)}</h2><p>{tr('Tell us about your property, the work you need and the timing that suits your business.','告诉我们物业位置、需要处理的问题，以及适合进场的时间。',lang)}</p>{button_link('/contact/',tr('Tell us about your property','告诉我们物业需求',lang),lang)}</div><div class="closing-art" aria-hidden="true"><div class="sunset-disc"></div><span>SUN.<br>SURF.<br>SERVICE.</span></div></section>'''

def faq_items(items, lang):
    return ''.join(f'<details data-faq data-filter-item data-tags="{e(x.get("category","planning"))}"><summary>{e(val(x,"q",lang))}<span aria-hidden="true">+</span></summary><div class="faq-answer"><p>{e(val(x,"a",lang))}</p></div></details>' for x in items)

def service_row(x, lang, i=0):
    return f'''<a href="{url('/services/'+x['slug']+'/',lang)}" class="service-row" data-filter-item data-tags="{SERVICE_GROUPS[x['slug']]}"><span class="service-mark mark-{i%4}" aria-hidden="true"></span><div><h3>{e(val(x,'title',lang))}</h3><p>{e(val(x,'short',lang))}</p></div><span class="row-view">{tr('Explore','查看',lang)}</span></a>'''

def sector_card(x,lang,i,full=False):
    return f'''<a href="{url('/sectors/'+x['slug']+'/',lang)}" class="sector-card color-{i%4}{' sector-full' if full else ''}" data-tilt data-filter-item data-tags="{e(x['slug'])}"><div class="sector-photo">{img(sector_image(i),val(x,'title',lang)+' — '+tr('illustrative property photograph','物业场景配图',lang))}</div><div class="sector-caption"><span class="eyebrow">{tr('PROPERTY CARE','商业物业维护',lang)}</span><h3>{e(val(x,'title',lang))}</h3><p>{e(val(x,'short',lang))}</p><span class="text-link">{tr('Explore this property type','查看对应维护内容',lang)}</span></div></a>'''

def article_card(x,lang,i):
    pic=['coast-hero.webp','sector-industrial.jpg','sector-hotel.jpg','sector-hotel.jpg','sector-hospitality.jpg','sector-retail.jpg'][i%6]
    return f'''<article class="news-card" data-tilt data-filter-item data-tags="{e('coastal' if i in [0,1,5] else 'planning')}"><a href="{url('/news/'+x['slug']+'/',lang)}"><div class="news-photo">{img(pic,val(x,'title',lang)+' — '+tr('illustrative image','场景配图',lang))}<span class="tag">{e(val(x,'category',lang))}</span></div><div class="news-copy"><h3>{e(val(x,'title',lang))}</h3><p>{e(val(x,'summary',lang))}</p><span class="text-link">{tr('Read the story','阅读全文',lang)}</span></div></a></article>'''

def process(lang):
    steps=[('Tell us what needs attention','说明维护事项','Send the property type, location, issue and useful photos.','提供物业类型、位置、问题描述及现场照片。'),('Agree the scope','确认范围与报价','We confirm the work, materials, access and quotation.','我们核对处理范围、材料、进场条件与报价。'),('Coordinate the visit','协调进场施工','We arrange the work around agreed operating and access times.','我们按确认的营业安排与通行时段组织施工。'),('Close out the work','核对完工交付','We record completed work and any items requiring follow-up.','我们整理完工记录，并说明需要后续跟进的项目。')]
    return '<ol class="process-list">'+''.join(f'<li data-reveal><span class="step-num">{i+1:02d}</span><h3>{tr(s[0],s[1],lang)}</h3><p>{tr(s[2],s[3],lang)}</p></li>' for i,s in enumerate(steps))+'</ol>'

def home(lang):
    from src.home_v2 import render
    body=render(lang, DATA, tr, e, val, url, img, a, button_link, service_row, sector_card, article_card, faq_items, process, cta)
    page('/',lang,tr('Gold Coast commercial property maintenance','黄金海岸商业物业维修与维护',lang),tr('Commercial repairs and maintenance for Gold Coast hotels, venues, workplaces and shared spaces.','黄金海岸酒店、餐饮、办公与公共区域的商业物业维修和维护。',lang),body,'page-home')


def page_intro(kicker,title,desc,lang,tone='aqua',image=None):
    return f'<section class="page-intro intro-{tone}"><div class="wrap intro-grid"><div><p class="eyebrow">{kicker}</p><h1>{title}</h1><p class="intro-lead">{desc}</p></div>'+('<div class="intro-photo">'+img(image,tr('Illustrative commercial property scene','商业物业场景配图',lang),'',True)+'</div>' if image else '<div class="intro-emblem" aria-hidden="true"><span class="sun-disc"></span><span>CARE<br>FOR THE<br>COAST.</span></div>')+'</div></section>'

def services_page(lang):
    buttons=[('all','All services','全部服务'),('buildings','Buildings','建筑'),('systems','Systems','设备系统'),('outdoors','Outdoor spaces','室外与环境')]
    body=page_intro(tr('GOLD COAST / OUR SERVICES','黄金海岸 / 服务内容',lang),tr('Commercial services.<br><em>Coastal care.</em>','商业物业维护。<br><em>每一项，都有安排。</em>',lang),tr('Commercial maintenance services for buildings, essential systems and outdoor spaces. One-off jobs and coordinated projects, with a clearly agreed scope.','建筑、设备与室外场地的商业维护服务。单项维修与多工种项目，都从明确范围开始。',lang),lang,'aqua','sector-hospitality.jpg')
    body+=f'<section class="section wrap" data-filter-group><div class="filter-bar" aria-label="{tr("Filter services","筛选服务",lang)}">'+''.join(f'<button data-filter="{k}" aria-pressed="{"true" if k=="all" else "false"}">{tr(en,zh,lang)}</button>' for k,en,zh in buttons)+'</div><div class="service-directory">'+''.join(service_row(x,lang,i) for i,x in enumerate(DATA['services']))+'</div></section>'+cta(lang)
    page('/services/',lang,tr('Commercial maintenance services','商业维护服务内容',lang),tr('Explore twelve categories of building, equipment and external maintenance for Gold Coast commercial properties.','查看黄金海岸商业物业的十二类建筑、设备与室外维护服务。',lang),body)

def related_services(slugs,lang):
    return '<div class="related-links">'+''.join(a('/services/'+s+'/',e(val(SERVICES[s],'title',lang)),lang) for s in slugs if s in SERVICES)+'</div>'

def service_detail(x,lang,i):
    title=val(x,'title',lang)
    group=SERVICE_GROUPS[x['slug']]
    pic={'buildings':'sector-retail.jpg','systems':'sector-office.jpg','outdoors':'sector-hospitality.jpg'}[group]
    body=page_intro(tr('GOLD COAST / COMMERCIAL SERVICES','黄金海岸 / 商业维护服务',lang),e(title),e(val(x,'intro',lang)),lang,'sand',pic)
    body+=f'<section class="section wrap detail-grid"><aside class="detail-sidebar"><p class="eyebrow">{tr("YOUR NEXT STEP","下一步安排",lang)}</p><h2>{tr("Let’s scope<br>the work.","先明确<br>需要做的工作。",lang)}</h2><p>{tr("Tell us the property type, issue and preferred timing.","提供物业类型、具体问题与期望时间。",lang)}</p>{button_link("/contact/?service="+x["slug"],tr("Prepare an enquiry","整理项目需求",lang),lang)}</aside><div><h2>{tr("What we can look after","我们处理的工作范围",lang)}</h2><ul class="scope-list">'+''.join(f'<li>{e(z)}</li>' for z in val(x,'items',lang))+'</ul><h2>'+tr('Planning the work','如何安排施工',lang)+'</h2><ol class="detail-process">'+''.join(f'<li>{e(z)}</li>' for z in val(x,'process',lang))+'</ol><h2>'+tr('Questions about this service','关于这项服务的问答',lang)+'</h2><div class="faq-list">'+faq_items(x['faq'],lang)+'</div></div></section>'
    related=[s['slug'] for s in DATA['services'] if SERVICE_GROUPS[s['slug']]==group and s['slug']!=x['slug']][:3]
    body+=f'<section class="related-section wrap"><p class="eyebrow">{tr("A JOINED-UP PLAN","关联服务",lang)}</p><h2>{tr("Other work to coordinate","可以一起协调的工作",lang)}</h2>{related_services(related,lang)}</section>'+cta(lang)
    page('/services/'+x['slug']+'/',lang,title+' · Gold Coast',val(x,'short',lang),body,'page-detail')

def sectors_page(lang):
    body=page_intro(tr('GOLD COAST / PROPERTY TYPES','黄金海岸 / 商业类型',lang),tr('Maintenance for<br>places to stay,<br><em>work & unwind.</em>','酒店与商业空间。<br>工作与经营场所。<br><em>按物业类型维护。</em>',lang),tr('A resort runs differently from a warehouse. We plan maintenance around the people, access and operations of each property.','酒店和仓库的运营方式不同。我们按物业用途、人员活动与进场条件安排维护。',lang),lang,'coral')
    body+='<section class="section wrap"><div class="sector-directory">'+''.join(sector_card(x,lang,i,True) for i,x in enumerate(DATA['sectors']))+'</div></section>'+cta(lang)
    page('/sectors/',lang,tr('Commercial property types','商业物业类型',lang),tr('Maintenance for hotels, body corporate, hospitality, retail, offices and industrial properties on the Gold Coast.','黄金海岸酒店、公寓共同物业、餐饮零售、办公和工业物业的维护内容。',lang),body)

def sector_detail(x,lang,i):
    body=page_intro(tr('GOLD COAST / PROPERTY CARE','黄金海岸 / 商业物业维护',lang),e(val(x,'title',lang)),e(val(x,'intro',lang)),lang,'coral',sector_image(i))
    body+=f'<section class="section wrap detail-grid"><div><p class="eyebrow">{tr("BUILT AROUND YOUR PROPERTY","围绕物业实际需求",lang)}</p><h2>{tr("The work behind<br>a well-kept space.","良好空间背后，<br>是具体的维护工作。",lang)}</h2></div><div><ul class="scope-list">'+''.join(f'<li>{e(z)}</li>' for z in val(x,'needs',lang))+'</ul><h2>'+tr('Relevant services','对应维护服务',lang)+'</h2>'+related_services(x['serviceSlugs'],lang)+'</div></section>'
    body+='<section class="section wrap">'+section_heading(tr('ACCESS & DELIVERY','进场与交付',lang),tr('A visit that fits<br>your operating day.','让进场安排，<br>衔接运营节奏。',lang),'',None,lang)+process(lang)+'</section>'+cta(lang)
    page('/sectors/'+x['slug']+'/',lang,val(x,'title',lang)+' · Gold Coast',val(x,'short',lang),body,'page-detail')

def news_page(lang):
    body=page_intro(tr('GOLD COAST / NEWS & IDEAS','黄金海岸 / 新闻与资讯',lang),tr('Notes from<br><em>the coast.</em>','来自海岸的<br><em>维护笔记。</em>',lang),tr('Practical reading on coastal exposure, property maintenance and planning work around your business.','围绕海岸环境、物业维修与营业安排，整理实用的维护内容。',lang),lang,'yellow','coast-hero.webp')
    body+=f'<section class="section wrap" data-filter-group><div class="filter-bar"><button data-filter="all" aria-pressed="true">{tr("All stories","全部文章",lang)}</button><button data-filter="coastal" aria-pressed="false">{tr("Coastal maintenance","海岸环境维护",lang)}</button><button data-filter="planning" aria-pressed="false">{tr("Property planning","物业施工安排",lang)}</button></div><div class="news-directory">'+''.join(article_card(x,lang,i) for i,x in enumerate(DATA['articles']))+'</div></section>'+cta(lang)
    page('/news/',lang,tr('Commercial property maintenance news','商业物业维护新闻与资讯',lang),tr('Ideas and guidance for Gold Coast commercial property maintenance.','黄金海岸商业物业维护与施工安排资讯。',lang),body)

def article_detail(x,lang,i):
    body=f'<article class="article-page"><header class="article-header wrap"><p class="eyebrow">{e(val(x,"category",lang))} / GOLD COAST</p><h1>{e(val(x,"title",lang))}</h1><p class="intro-lead">{e(val(x,"summary",lang))}</p><p class="article-byline">{tr("Ellis Services Group · Maintenance notes","Ellis Services Group · 物业维护笔记",lang)}</p></header><div class="article-hero wrap">{img(["coast-hero.webp","sector-industrial.jpg","sector-hotel.jpg","sector-hotel.jpg","sector-hospitality.jpg","sector-retail.jpg"][i%6],tr("Illustrative property photograph","物业场景配图",lang),"",True)}</div><div class="article-body">'+''.join(f'<p>{e(z)}</p>' for z in val(x,'body',lang))
    if x.get('sourceUrls'):
        body+=f'<div class="article-sources"><h2>{tr("Source references","参考来源",lang)}</h2><ul>'+''.join(f'<li><a href="{e(s)}" target="_blank" rel="noopener noreferrer">{e(s.split("/")[2])}</a></li>' for s in x['sourceUrls'])+'</ul></div>'
    body+='<h2>'+tr('Services connected to this topic','与本话题相关的服务',lang)+'</h2>'+related_services(x['serviceSlugs'],lang)+'</div></article>'+cta(lang)
    page('/news/'+x['slug']+'/',lang,val(x,'title',lang),val(x,'summary',lang),body,'page-article')

def faq_page(lang):
    body=page_intro(tr('GOLD COAST / FREQUENTLY ASKED QUESTIONS','黄金海岸 / 常见问题',lang),tr('Good questions.<br><em>Clear answers.</em>','把问题问清楚。<br><em>把安排说明白。</em>',lang),tr('Work scope, property access, scheduling and the details we need to plan your maintenance.','工作范围、物业进场、施工时间，以及安排维护所需的信息。',lang),lang,'aqua')
    body+=f'<section class="section wrap faq-page-content" data-filter-group><div class="faq-tools"><label for="faq-search">{tr("Find an answer","查找问题",lang)}</label><input id="faq-search" type="search" placeholder="{tr("Try access, photos or hours…","搜索进场、照片、营业时间…",lang)}"><div class="filter-bar"><button data-filter="all" aria-pressed="true">{tr("All questions","全部问题",lang)}</button><button data-filter="planning" aria-pressed="false">{tr("Planning","施工安排",lang)}</button><button data-filter="scope" aria-pressed="false">{tr("Work scope","工作范围",lang)}</button><button data-filter="coastal" aria-pressed="false">{tr("Coastal properties","海岸物业",lang)}</button></div><p data-result-count aria-live="polite"></p></div><p data-no-results hidden role="status">{tr("No matching questions. Try another search or choose All questions.","未找到对应问题。修改搜索内容，或选择全部问题。",lang)}</p><div class="faq-list">{faq_items(DATA["faqs"],lang)}</div></section>'+cta(lang)
    page('/faq/',lang,tr('Commercial maintenance FAQ','商业维护常见问题',lang),tr('Answers about maintenance scope, quoting, access and scheduling for Gold Coast commercial properties.','黄金海岸商业物业维修范围、报价、进场与施工安排问答。',lang),body)

def about_page(lang):
    body=page_intro(tr('ELLIS SERVICES GROUP / GOLD COAST','ELLIS SERVICES GROUP / 黄金海岸',lang),tr('Coastal spirit.<br><em>Practical care.</em>','明快的海岸气息。<br><em>具体的物业维护。</em>',lang),tr('We bring building repairs, essential systems and outdoor maintenance into one coordinated scope.','我们把建筑维修、设备系统和室外环境维护，纳入统一的项目安排。',lang),lang,'sand','sector-office.jpg')
    body+=f'<section class="section wrap about-story"><div data-reveal><p class="eyebrow">{tr("ONE PROPERTY. ONE CLEAR PLAN.","一处物业，一份清楚的安排。",lang)}</p><h2>{tr("Care for the place.<br>Consider the people.","照顾物业，<br>也衔接现场日常。",lang)}</h2></div><div class="prose" data-reveal><p>{tr("We work with property managers, business owners and site contacts to identify what needs attention and how the work should be organised. A small repair, a planned maintenance visit or a project involving several trades starts with a clear scope.","我们与物业经理、经营者及现场联系人沟通，确认需要处理的事项与施工条件。无论是单次维修、定期维护还是多工种项目，都从明确的工作范围开始。",lang)}</p><p>{tr("We confirm access, materials, work areas and the order of tasks before arranging the visit. At completion, we record the agreed work and identify any further items for the property manager to consider.","进场前，我们确认通行、材料、作业区域与施工顺序。完成后整理已确认范围内的工作记录，并说明需要后续跟进的事项。",lang)}</p></div></section><section class="about-values"><div class="wrap value-grid"><article><span class="eyebrow">{tr("SCOPE","范围",lang)}</span><h2>{tr("Know what’s included.","做什么，先说清楚。",lang)}</h2><p>{tr("A useful quotation explains the work, access assumptions and inclusions.","报价说明工作内容、进场条件与包含项目。",lang)}</p></article><article><span class="eyebrow">{tr("COORDINATION","协调",lang)}</span><h2>{tr("Make the visit count.","进一次场，安排到位。",lang)}</h2><p>{tr("We bring related tasks together and agree their sequence around your property.","关联事项集中梳理，结合物业安排确认施工顺序。",lang)}</p></article><article><span class="eyebrow">{tr("HANDOVER","交付",lang)}</span><h2>{tr("Leave a useful record.","做完，有记录。",lang)}</h2><p>{tr("Completed work, supporting photos and follow-up items are clearly identified.","完工内容、对应照片与后续事项分别记录清楚。",lang)}</p></article></div></section><section class="section wrap">{section_heading(tr("HOW THE WORK COMES TOGETHER","从需求到完工",lang),tr("From first conversation<br>to a clear handover.","从第一次沟通，<br>到明确的完工交付。",lang),"",None,lang)}{process(lang)}</section>'+cta(lang)
    page('/about/',lang,tr('About Ellis commercial property care','关于 Ellis 商业物业维护',lang),tr('Building, system and outdoor maintenance coordinated around Gold Coast commercial properties.','围绕黄金海岸商业物业，统一安排建筑、设备与室外维护。',lang),body)

def contact_page(lang):
    service_options=''.join(f'<option value="{x["slug"]}">{e(val(x,"title",lang))}</option>' for x in DATA['services'])
    sector_options=''.join(f'<option value="{x["slug"]}">{e(val(x,"title",lang))}</option>' for x in DATA['sectors'])
    req=tr('Required','必填',lang)
    body=f'''<section class="contact-section wrap"><div class="contact-copy"><p class="eyebrow">{tr('GOLD COAST / LET’S TALK PROPERTY','黄金海岸 / 联系我们',lang)}</p><h1>{tr('Tell us what<br>needs a little<br><em>attention.</em>','说说你的物业，<br>有哪些需要<br><em>处理的问题。</em>',lang)}</h1><p class="intro-lead">{tr('Start with the property, the problem and the timing. We can build the scope from there.','从物业类型、具体问题和期望时间开始，梳理这次需要处理的工作。',lang)}</p><div class="contact-note"><h2>{tr('Useful details to include','可以一起提供的信息',lang)}</h2><ul><li>{tr('Property type and Gold Coast suburb','物业类型与黄金海岸所在区域',lang)}</li><li>{tr('The affected area and what has changed','出现问题的部位与具体情况',lang)}</li><li>{tr('Access times and your site contact','可进场时段及现场联系人',lang)}</li><li>{tr('Photos, if available','现场照片（如有）',lang)}</li></ul></div><div class="contact-photo">{img('coast-hero.webp',tr('Illustrative coastal setting','海岸场景设计配图',lang))}</div></div>
    <div class="form-panel"><form id="enquiry-form"><p class="eyebrow">{tr('YOUR PROPERTY DETAILS','项目需求',lang)}</p><h2>{tr('Let’s make a plan.','把维护安排起来。',lang)}</h2><p id="enquiry-notice" class="form-note">{tr('Design preview: this form prepares an enquiry in your browser. It does not send it to Ellis.','设计预览：表单将在本浏览器生成需求草稿，不会发送给 Ellis。',lang)}</p><div class="form-grid"><div><label for="name">{tr('Your name','姓名',lang)} <span>*</span></label><input id="name" name="name" autocomplete="name" required maxlength="100"></div><div><label for="email">{tr('Email address','邮箱',lang)} <span>*</span></label><input id="email" name="email" type="email" autocomplete="email" required maxlength="200"></div><div><label for="suburb">{tr('Property suburb','物业所在区域',lang)} <span>*</span></label><input id="suburb" name="suburb" autocomplete="address-level2" required maxlength="100" placeholder="{tr('e.g. Broadbeach','例如 Broadbeach',lang)}"></div><div><label for="property">{tr('Property type','物业类型',lang)} <span>*</span></label><select id="property" name="property" required><option value="">{tr('Select a property type','选择物业类型',lang)}</option>{sector_options}</select></div><div class="field-full"><label for="service">{tr('What kind of work?','需要哪类工作？',lang)}</label><select id="service" name="service"><option value="">{tr('Several jobs / not sure yet','多项工作 / 尚未确定',lang)}</option>{service_options}</select></div><div class="field-full"><label for="message">{tr('Tell us about the issue','描述需要处理的问题',lang)} <span>*</span></label><textarea id="message" name="message" required rows="5" maxlength="6000" placeholder="{tr('What needs attention? When can the property be accessed?','具体哪些部位需要处理？什么时间方便进场？',lang)}"></textarea></div><div class="field-full"><label for="photos">{tr('Photos (optional)','现场照片（可选）',lang)}</label><input type="file" id="photos" name="photos" accept="image/jpeg,image/png,image/webp" multiple><p class="input-help">{tr('Up to 5 JPG, PNG or WebP images, 10 MB each. Photos stay in this browser.','最多5张 JPG、PNG 或 WebP，每张不超过10MB；照片仅在本浏览器使用。',lang)}</p><ul id="photo-list"></ul></div></div><button class="button" type="submit">{tr('Prepare enquiry','生成需求草稿',lang)}</button></form><section id="enquiry-result" hidden tabindex="-1"><p class="eyebrow">{tr('YOUR ENQUIRY DRAFT','需求草稿',lang)}</p><h2>{tr('Details, brought together.','需求已经整理好。',lang)}</h2><p role="status" data-enquiry-status>{tr('Draft prepared in this browser. No enquiry has been sent.','需求草稿已在本浏览器生成，尚未发送。',lang)}</p><pre id="enquiry-summary"></pre><div class="button-row"><button type="button" id="download-enquiry" class="button">{tr('Download draft','下载草稿',lang)}</button><button type="button" id="copy-enquiry" class="button button-outline">{tr('Copy details','复制内容',lang)}</button><button type="button" id="edit-enquiry" class="text-button">{tr('Edit details','修改需求',lang)}</button></div></section></div></section>'''
    page('/contact/',lang,tr('Contact · Plan commercial maintenance','联系我们 · 安排商业物业维护',lang),tr('Prepare a maintenance enquiry for your Gold Coast commercial property.','整理黄金海岸商业物业维修与维护需求。',lang),body,'page-contact')

def credits(lang):
    sources=json.loads((ROOT/'src/assets-sources.json').read_text(encoding="utf-8")) if (ROOT/'src/assets-sources.json').exists() else {}
    body=page_intro(tr('IMAGE CREDITS','图片说明',lang),tr('Scenes of<br><em>coastal life.</em>','关于这些<br><em>海岸场景。</em>',lang),tr('Images in this design are illustrative, not records of Ellis projects.','本设计中的图片用于展示场景，不作为 Ellis 完工项目记录。',lang),lang,'sand')
    body+='<section class="section wrap prose"><h2>'+tr('Coastal hero image','首页海岸主视觉',lang)+'</h2><p>'+tr('Generated specifically for this design. The scene is illustrative and does not identify a real venue or client.','为本次设计生成的海岸场景，不代表特定场地或客户项目。',lang)+'</p><h2>'+tr('Property photography','物业场景摄影',lang)+'</h2><p>Nico Smit · Johan Mouchet · ANNIE HATUANH · Alesia Kazantceva · Mathias Reding / Unsplash</p><p>'+tr('Hotel, café, retail, office and industrial photographs are stock imagery. Their locations are not presented as verified Gold Coast sites.','酒店、咖啡馆、零售、办公和工业照片为图库配图，不标注为已核实的黄金海岸地点。',lang)+'</p></section>'
    page('/image-credits/',lang,tr('Image credits','图片说明',lang),tr('Image sources and design imagery.','海岸设计图片、图库摄影与来源说明。',lang),body)

for lang in ['en','zh']:
    home(lang); services_page(lang); sectors_page(lang); news_page(lang); faq_page(lang); about_page(lang); contact_page(lang); credits(lang)
    for i,x in enumerate(DATA['services']): service_detail(x,lang,i)
    for i,x in enumerate(DATA['sectors']): sector_detail(x,lang,i)
    for i,x in enumerate(DATA['articles']): article_detail(x,lang,i)

(OUT/'404.html').write_text('''<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Page not found | Ellis Gold Coast</title><meta name="description" content="This page is not available. Return to Ellis Gold Coast commercial property maintenance."><meta name="robots" content="noindex"><meta name="theme-color" content="#FF642D"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/surf-font.css"><link rel="stylesheet" href="/chinese-font.css"><link rel="stylesheet" href="/maximal.css"><style>body.page-not-found{min-height:100svh;display:grid;place-items:center;padding:35px 22px;background:var(--gc-orange)}body.page-not-found .not-found{width:min(900px,100%);margin:0;padding:clamp(30px,7vw,90px);background:var(--gc-sun);border:3px solid var(--gc-ink);box-shadow:12px 12px 0 var(--gc-ink);text-align:left}body.page-not-found .error-code{display:inline-block;background:var(--gc-pink);border:2px solid var(--gc-ink);padding:7px 20px;font-family:var(--gc-display);font-size:2rem;transform:rotate(-4deg);margin-bottom:28px}body.page-not-found h1{font-size:clamp(2.3rem,8vw,5.6rem);line-height:1.06;overflow-wrap:break-word}body.page-not-found .error-actions{display:flex;align-items:center;flex-wrap:wrap;gap:22px;margin-top:30px}body.page-not-found .button{background:var(--gc-aqua);color:var(--gc-ink)}body.page-not-found .button:hover{background:var(--gc-pink)}</style></head><body class="maximal page-not-found"><main id="main" class="not-found"><p class="eyebrow">ELLIS / GOLD COAST</p><span class="error-code" aria-label="Error 404">404</span><h1>This path<br>ends here.</h1><p>The page you are looking for is not available.</p><div class="error-actions"><a class="button" href="/">Back to home</a><a class="text-link" href="/zh/" lang="zh-CN">返回中文首页</a></div></main></body></html>''', encoding="utf-8", newline="\n")
(OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n', encoding="utf-8", newline="\n")
(OUT/'assets/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="18" fill="#FFE34D"/><circle cx="32" cy="32" r="15" fill="#241611"/><path d="M32 7v5M32 52v5M7 32h5M52 32h5M14 14l4 4M46 46l4 4M14 50l4-4M46 18l4-4" stroke="#241611" stroke-width="4"/></svg>', encoding="utf-8", newline="\n")
print(json.dumps({'html_pages':len(list(OUT.rglob('*.html'))),'services':len(DATA['services']),'sectors':len(DATA['sectors']),'articles':len(DATA['articles'])}))
