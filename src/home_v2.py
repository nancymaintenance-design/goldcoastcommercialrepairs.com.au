"""Gold Coast surf-poster homepage. Content helpers are supplied by build.py."""

def render(lang, data, tr, e, val, url, img, a, button_link, service_row, sector_card, article_card, faq_items, process, cta):
    def t(en, zh): return tr(en, zh, lang)
    stripe_words = t('BUSINESS. PROPERTY. PROFESSIONAL MAINTENANCE.', '商业。地产。专业维护。')
    loop = ''.join(f'<span>{stripe_words}</span><span aria-hidden="true">✳</span>' for _ in range(4))
    work_loop = ''.join(f'<span>{t("BUILDINGS / SYSTEMS / OUTDOORS", "建筑 / 设备 / 室外空间")}</span><span aria-hidden="true">✳</span>' for _ in range(3))
    wave = '<svg viewBox="0 0 1440 120" preserveAspectRatio="none" aria-hidden="true"><path d="M0,58 C180,140 300,-20 510,52 C720,125 810,8 1015,50 C1220,100 1290,20 1440,60 L1440,120 L0,120 Z"/></svg>'
    service_by_slug = {item['slug']: item for item in data['services']}
    faq_by_id = {item['id']: item for item in data['faqs']}
    services = ''.join(service_row(service_by_slug[slug],lang,j) for j,slug in enumerate(data['home']['featuredServices']))
    featured_faqs = [faq_by_id[id] for id in data['home']['featuredFaqs']]
    work_modes = ''.join(
        f'<li><h3>{e(val(item,"title",lang))}</h3><p>{e(val(item,"text",lang))}</p>'
        f'{a(item["path"],t("Explore the work","查看相关工作"),lang,"text-link")}</li>'
        for item in data['home']['workModes']
    )
    sectors = ''.join(sector_card(x,lang,i) for i,x in enumerate(data['sectors']))
    news = ''.join(article_card(x,lang,i) for i,x in enumerate(data['articles']))
    return f'''
    <section class="hero-scroll" data-tide>
      <div class="hero">
        <div class="hero-scene">{img('coast-hero.webp',t('Sunny Gold Coast shoreline with beach club, striped umbrellas and adult holidaymakers','阳光下的黄金海岸、沙滩俱乐部、条纹遮阳伞与成年游客的设计配图'),'',True)}</div>
        <div class="hero-shade" aria-hidden="true"></div>
        <div class="hero-copy">
          <p class="eyebrow hero-eyebrow">ELLIS / GOLD COAST<br>{t('COMMERCIAL PROPERTY CARE','黄金海岸商业物业服务')}</p>
          <h1 class="hero-city hero-headline"><span>{t('COMMERCIAL REPAIRS','商业维修')}</span>
            <span>{t('PROPERTY MAINTENANCE','物业维护')}</span></h1>
          <p class="hero-service">{t('HOTELS · SHOPS · OFFICES','酒店 · 商铺 · 办公室')}<br>{t('DAY-TO-DAY REPAIRS · FACILITY FIXES · PLANNED MAINTENANCE','日常维修 · 设施修补 · 计划维护')}</p>
          <div class="hero-actions">{button_link('/contact/',t('LET’S PLAN THE WORK','安排物业维护'),lang)}{a('/services/',t('EXPLORE SERVICES','浏览服务内容'),lang,'hero-service-link')}</div>
        </div>
        <div class="hero-sun" aria-hidden="true"><div class="sun-rays"></div><div class="sun-lettering">SUN<br>SURF<br>SERVICE</div></div>
        <div class="hero-note" data-tilt><span class="eyebrow">{t('GOOD SPACES. GREAT DAYS.','海岸的活力，物业的好状态。')}</span><p>{t('We keep the coast’s<br>working spaces<br>in good shape.','我们照顾海岸的<br>商业空间，<br>让日常运转有序。')}</p><span class="note-line">{t('HOTELS · VENUES · WORKPLACES','酒店 · 餐饮 · 办公与商业物业')}</span></div>
        <div class="hero-bottom"><span>{t('REPAIRS / MAINTENANCE / MULTI-TRADE','单项维修 / 定期维护 / 多工种项目')}</span><span class="scroll-cue">{t('SCROLL INTO THE COAST','向下探索海岸维护')} <i aria-hidden="true"></i></span></div>
        <div class="hero-wave" aria-hidden="true">{wave}</div>
      </div>
    </section>
    <section class="ribbon-crossing" aria-label="{t('Buildings, systems and outdoor spaces','建筑、设备与室外空间')}"><div class="ribbon ribbon-back" aria-hidden="true"><div class="marquee-line">{work_loop}{work_loop}</div></div><div class="ribbon ribbon-front" aria-hidden="true"><div class="marquee-line">{loop}{loop}</div></div></section>
    <section class="section home-services" id="services">
      <div class="wrap"><div class="section-heading" data-reveal><div><p class="eyebrow">{t('TWELVE SERVICES. ONE COORDINATED PLAN.','十二类服务，统一安排。')}</p><h2>{t('BIG CARE.<br>EVERY<br><em>DETAIL.</em>','大到建筑，<br>小到每个<br><em>维护细节。</em>')}</h2></div><div class="section-intro"><span class="surf-asterisk" aria-hidden="true">✳</span><p>{t('We look after the buildings, systems and outdoor spaces behind your working day.','我们处理商业建筑、设备系统与室外环境的维修，让维护安排衔接物业日常运营。')}</p>{a('/services/',t('VIEW ALL 12 SERVICES','查看全部十二类服务'),lang,'text-link')}</div></div>
      <div class="home-service-layout"><div class="service-feature" data-parallax data-tilt><div class="feature-tape">{t('A LITTLE SUN. A LOT OF CARE.','阳光之下，细致维护。')}</div>{img('sector-hotel.jpg',t('Hotel pool and outdoor commercial space','酒店泳池与室外商业空间图库配图'))}<div class="feature-label"><p>{t('BUILT FOR<br>COASTAL<br>BUSINESS.','为海岸<br>商业空间<br>安排维护。')}</p></div></div><div class="service-list">{services}</div></div></div>
    </section>
    <section class="section content-work-modes"><div class="wrap"><h2>{t('What work are you planning?', '这次需要安排什么工作？')}</h2><ul class="process-list">{work_modes}</ul></div></section>
    <section class="sector-section" data-carousel data-pin-gallery>
      <div class="pin-inner"><div class="wrap"><div class="section-heading" data-reveal><div><p class="eyebrow">{t('EIGHT PROPERTY TYPES. DIFFERENT WORKING DAYS.','八类商业物业，各有运营节奏。')}</p><h2>{t('LIFE ON<br><em>THE COAST.</em>','海岸生活，<br><em>商业日常。</em>')}</h2></div><div class="section-intro"><p>{t('From the first coffee to the last check-in. Explore care for the spaces people use.','从早上的第一杯咖啡，到晚上的最后一位住客，查看各类商业物业的维护内容。')}</p>{a('/sectors/',t('EXPLORE PROPERTY TYPES','查看商业类型'),lang,'text-link')}</div></div><div class="gallery-toolbar"><span class="gallery-caption">{t('SCROLL TO EXPLORE THE COLLECTION','向下滚动，展开商业场景')}</span><div class="carousel-controls"><button data-prev aria-label="{t('Previous property','上一类物业')}">{t('PREVIOUS','上一组')}</button><button data-next aria-label="{t('Next property','下一类物业')}">{t('NEXT','下一组')}</button></div></div></div><div class="carousel-track" data-track>{sectors}</div></div>
    </section>
    <section class="coastal-section" data-tide><div class="wave-transition" aria-hidden="true">{wave}</div><div class="wrap coastal-grid"><div class="coastal-type" data-reveal><p class="eyebrow">{t('A COASTAL ADDRESS CHANGES THE PLAN','海岸环境，写进维护计划。')}</p><h2><span>{t('SALT.','海风。')}</span><span>{t('SUN.','日晒。')}</span><span>{t('STORMS.','骤雨。')}</span></h2><div class="weather-disc" aria-hidden="true"><div class="umbrella-lines"></div><span>GOLD<br>COAST<br>CARE</span></div></div><div class="coastal-issues"><article data-reveal><span class="issue-icon" aria-hidden="true">≈</span><div><h3>{t('SALT AIR & EXPOSED SURFACES','海盐与建筑暴露部位')}</h3><p>{t('We check finishes and fixings on exposed elevations, under eaves and around sheltered entrances beyond the reach of normal rainfall. Cleaning and repair scopes follow the material and its condition.','我们核对外露立面、檐下和避雨入口，查看涂层与固定件是否积盐或受损，根据实际材料与状态安排清洁和维修。')}</p></div></article><article data-reveal><span class="issue-icon" aria-hidden="true">☂</span><div><h3>{t('RAIN, FROM ROOF TO GROUND','从屋面到地面的雨水路径')}</h3><p>{t('We consider roof junctions, gutters, downpipes and ground drainage together when tracing water ingress.','漏水排查结合屋面节点、天沟、落水管与地面排水一并展开。')}</p></div></article><article data-reveal><span class="issue-icon" aria-hidden="true">☼</span><div><h3>{t('OUTDOOR LIFE. WORKING SPACES.','持续使用的室外空间')}</h3><p>{t('Terraces, doors, paving and shared areas need a work plan that accounts for guest access, trading and everyday use.','露台、门窗、铺装和公共区域维护，结合住客通行、营业与日常使用安排。')}</p></div></article>{a('/news/',t('READ THE COASTAL NOTES','阅读海岸维护资讯'),lang,'text-link')}</div></div></section>
    <section class="section process-section"><div class="wrap"> <div class="section-heading" data-reveal><div><p class="eyebrow">{t('LESS TO CHASE. MORE CLEARLY ARRANGED.','从需求到交付，安排清楚。')}</p><h2>{t('LET’S MAKE<br><em>IT HAPPEN.</em>','一起把工作<br><em>安排到位。</em>')}</h2></div><div class="section-intro"><p>{t('A defined scope. Agreed access. Coordinated work. A useful handover.','明确工作范围，确认进场条件，协调施工顺序，整理完工记录。')}</p></div></div>{process(lang)}</div></section>
    <section class="section news-section" data-carousel><div class="wrap"><div class="section-heading" data-reveal><div><p class="eyebrow">{t('FROM THE COAST / MAINTENANCE JOURNAL','来自海岸 / 维护笔记')}</p><h2>{t('FRESH<br><em>OFF THE COAST.</em>','海岸日常，<br><em>维护新知。</em>')}</h2></div><div class="section-intro">{a('/news/',t('EXPLORE THE JOURNAL','查看全部新闻'),lang,'text-link')}<div class="carousel-controls"><button data-prev>{t('PREVIOUS','上一组')}</button><button data-next>{t('NEXT','下一组')}</button></div></div></div><div class="news-track" data-track>{news}</div></div></section>
    <section class="section faq-home"><div class="wrap faq-home-grid"><div data-reveal><p class="eyebrow">{t('A FEW THINGS, CLEARED UP.','把问题问清楚，把安排说明白。')}</p><h2>{t('GOOD<br><em>QUESTIONS.</em>','关于维护，<br><em>你会想问。</em>')}</h2>{a('/faq/',t('ALL YOUR QUESTIONS','查看全部常见问题'),lang,'text-link')}<div class="faq-sun" aria-hidden="true">✺</div></div><div class="faq-list">{faq_items(featured_faqs,lang)}</div></div></section>
    {cta(lang)}
    '''
