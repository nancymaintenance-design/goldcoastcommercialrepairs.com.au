"""A shared Gold Coast service-desk finale, using the existing motion layer."""


def render_cta(lang, tr, url):
    lines = tr(
        ('BIG PLANS.', 'SMALL FIXES.', 'LET’S TALK.'),
        ('大到项目，', '小到维修，', '我们来安排。'), lang
    )
    title = ''.join(
        f'<span class="coast-outro__line coast-outro__line--{i}" data-reveal>'
        f'<span class="coast-outro__word">{line}</span></span>'
        for i, line in enumerate(lines)
    )
    return f'''<section class="coast-outro" id="coast-outro" aria-labelledby="coast-outro-title" data-tide>
      <div class="coast-outro__stripe" aria-hidden="true"></div>
      <div class="coast-outro__inner">
        <div class="coast-outro__copy">
          <p class="coast-outro__eyebrow">{tr('YOUR PROPERTY. OUR NEXT CONVERSATION.', '你的物业，我们一起安排。', lang)}</p>
          <h2 class="coast-outro__title" id="coast-outro-title">{title}</h2>
          <p class="coast-outro__body">{tr('Tell us what needs attention. We’ll work through the scope, access and timing with you.', '告诉我们需要处理的问题，我们一起确认工作范围、进场条件与时间安排。', lang)}</p>
          <a class="coast-outro__link" href="{url('/contact/', lang)}">{tr('Tell us about your property', '告诉我们物业需求', lang)}</a>
        </div>
        <div class="coast-outro__scene">
          <div class="coast-outro__board" aria-hidden="true"><span>GOLD<br>COAST</span></div>
          <figure class="coast-outro__photo">
            <img src="/assets/sector-hospitality.jpg" alt="{tr('Sunny outdoor hospitality terrace', '阳光下的露天餐饮空间，场景配图', lang)}" width="1080" height="720" loading="lazy" decoding="async">
          </figure>
          <a class="coast-outro__contact" href="{url('/contact/', lang)}" data-magnetic aria-label="{tr('Let’s talk about your property', '联系我们，安排物业维护', lang)}">
            <span class="coast-outro__disc" data-tilt>
              <svg class="coast-outro__ring" viewBox="0 0 200 200" aria-hidden="true"><defs><path id="coast-contact-ring" d="M100,100 m-76,0 a76,76 0 1,1 152,0 a76,76 0 1,1 -152,0"/></defs><text><textPath href="#coast-contact-ring" textLength="468" lengthAdjust="spacing">LET’S MAKE A PLAN · GOLD COAST · </textPath></text></svg>
              <span class="coast-outro__contact-label">{tr('LET’S<br>TALK', '联系<br>我们', lang)}</span>
            </span>
          </a>
          <span class="coast-outro__scene-note">{tr('COMMERCIAL PROPERTY CARE', '商业物业 · 维修与维护', lang)}</span>
        </div>
      </div>
      <svg class="coast-outro__wave" viewBox="0 0 1600 95" preserveAspectRatio="none" aria-hidden="true"><path class="coast-outro__wave-back" d="M-100 60 Q100 0 300 50 T700 50 T1100 50 T1500 50 T1900 50 V100 H-100Z"/><path class="coast-outro__wave-front" d="M-100 82 Q100 22 300 72 T700 72 T1100 72 T1500 72 T1900 72 V100 H-100Z"/></svg>
    </section>'''


def render_footer(lang, tr, url, nav):
    links = ''.join(
        f'<a class="shore-footer__nav-link shore-footer__nav-link--{i}" href="{url(path, lang)}"><span>{tr(en, zh, lang)}</span></a>'
        for i, (path, en, zh) in enumerate(nav[1:])
    )
    letters = ''.join(f'<span class="shore-footer__letter" style="--letter:{i}">{letter}</span>' for i, letter in enumerate('ELLIS'))
    return f'''<footer class="shore-footer" id="shore-footer" data-tide>
      <div class="shore-footer__inner">
        <div class="shore-footer__topline"><p>GOLD COAST, QUEENSLAND</p><p>{tr('BUILDINGS. SYSTEMS. OUTDOOR SPACES.', '建筑 · 设备 · 室外空间', lang)}</p></div>
        <nav class="shore-footer__nav" aria-label="{tr('Footer navigation', '页脚导航', lang)}">{links}</nav>
        <div class="shore-footer__brand-wrap" data-reveal>
          <a class="shore-footer__brand" href="{url('/', lang)}" aria-label="{tr('Ellis Gold Coast — back to home', 'Ellis 黄金海岸，返回首页', lang)}"><span class="shore-footer__letters" aria-hidden="true">{letters}</span></a>
          <span class="shore-footer__brand-caption">{tr('A LITTLE COASTAL SPIRIT. A LOT OF PROPERTY CARE.', '把海岸的明快，带进物业的日常。', lang)}</span>
        </div>
        <div class="shore-footer__legal"><span>© 2026 Ellis Services Group</span><a href="{url('/image-credits/', lang)}">{tr('Image credits', '图片说明', lang)}</a></div>
      </div>
      <div class="shore-footer__hem" aria-hidden="true"></div>
    </footer>'''

def render_detail_footer(lang, tr, url, nav, brand):
    links = ''.join(f'<a href="{url(path, lang)}">{tr(en, zh, lang)}</a>' for path, en, zh in nav)
    return f'''<footer class="gc-detail-footer" id="shore-footer">
      <div class="gc-detail-footer__row">{brand}
        <nav aria-label="{tr('Footer navigation', '页脚导航', lang)}">{links}</nav>
      </div>
      <div class="gc-detail-footer__legal"><span>© 2026 Ellis Services Group</span>
        <a href="{url('/image-credits/', lang)}">{tr('Image credits', '图片说明', lang)}</a>
      </div>
    </footer>'''
