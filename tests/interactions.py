"""Exercise existing interactions in Chromium, without sending any enquiry."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_audit import BASE, CHROME, ROOT, REPORTS

checks = []
def check(name, condition, detail=None):
    checks.append({'name': name, 'passed': bool(condition), 'detail': detail})

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, headless=True)
        context = browser.new_context(permissions=['clipboard-read', 'clipboard-write'], viewport={'width':1440,'height':960})
        page = context.new_page()
        for lang in ['', '/zh']:
            page.goto(BASE+lang+'/services/')
            page.locator('[data-filter="systems"]').click()
            check(lang+' service systems filter',page.locator('.service-row:visible').count()==4)
            page.locator('[data-filter="all"]').click()
            check(lang+' service reset',page.locator('.service-row:visible').count()==12)
            page.goto(BASE+lang+'/news/')
            page.locator('[data-filter="coastal"]').click()
            check(lang+' news filter',page.locator('.news-card:visible').count()==3)
            page.goto(BASE+lang+'/faq/')
            page.locator('#faq-search').fill('海盐' if lang else 'salt')
            check(lang+' faq search', page.locator('[data-faq]:visible').count()==1)
            page.locator('[data-faq]:visible summary').click()
            check(lang+' faq disclosure',page.locator('[data-faq]:visible').get_attribute('open') is not None)
            page.locator('#faq-search').fill('zzzzunmatched')
            check(lang+' faq no results',page.locator('[data-no-results]').is_visible())
            page.goto(BASE+lang+'/contact/?service=roofing-waterproofing&property=hotels-resorts')
            check(lang+' service enquiry link',page.locator('#service').input_value()=='roofing-waterproofing')
            page.locator('button[type=submit]').click()
            check(lang+' empty form blocked',page.locator('#enquiry-result').is_hidden())
            for field,value in [('name','TEST local preview'),('email','invalid'),('suburb','Broadbeach'),('message','TEST only, local draft. No dispatch.')]:
                page.locator('#'+field).fill(value)
            page.locator('#property').select_option(index=1)
            check(lang+' invalid email blocked',not page.locator('#email').evaluate('(e)=>e.checkValidity()'))
            page.locator('#email').fill('test@example.com')
            check(lang+' property enquiry link',page.locator('#property').input_value()=='hotels-resorts')
            check(lang+' no upload without a receiving endpoint',page.locator('input[type=file]').count()==0)
            page.locator('#access-window').fill('Tuesday 7 to 9 am')
            page.locator('button[type=submit]').click()
            check(lang+' local draft generated',page.locator('#enquiry-result').is_visible() and 'Tuesday 7 to 9 am' in page.locator('#enquiry-summary').inner_text())
            page.locator('#copy-enquiry').click()
            page.wait_for_function("navigator.clipboard.readText().then(text => text.includes('Tuesday 7 to 9 am'))")
            check(lang+' access window in copied draft','Tuesday 7 to 9 am' in page.evaluate('navigator.clipboard.readText()'))
            with page.expect_download() as download:
                page.locator('#download-enquiry').click()
            check(lang+' draft download',download.value.suggested_filename=='gold-coast-work-summary.txt' and 'Tuesday 7 to 9 am' in Path(download.value.path()).read_text(encoding='utf-8'))
            page.locator('#edit-enquiry').click()
            check(lang+' edit retained',page.locator('#name').input_value()=='TEST local preview' and page.locator('#enquiry-result').is_hidden())
            page.set_viewport_size({'width':390,'height':844})
            page.goto(BASE+lang+'/')
            page.locator('.menu-toggle').click()
            check(lang+' menu seven links',page.locator('#primary-nav a:visible').count()==7)
            page.keyboard.press('Escape')
            check(lang+' escape closes menu',page.locator('.menu-toggle').get_attribute('aria-expanded')=='false')
            check(lang+' language route', page.locator('.lang-switch').get_attribute('href')==('/' if lang else '/zh/'))
            for selector in ['.sector-section','.news-section']:
                section=page.locator(selector)
                section.scroll_into_view_if_needed()
                section.locator('[data-next]').click()
                page.wait_for_timeout(700)
                left=section.locator('[data-track]').evaluate('(e)=>e.scrollLeft')
                check(lang+' mobile next '+selector,left>100,left)
                section.locator('[data-prev]').click()
                page.wait_for_timeout(700)
                check(lang+' mobile previous '+selector,section.locator('[data-track]').evaluate('(e)=>e.scrollLeft')<left)
        page.set_viewport_size({'width':1440,'height':960})
        page.goto(BASE+'/')
        page.wait_for_timeout(1400)
        for progress in [0,.5,1]:
            y=page.locator('[data-pin-gallery]').evaluate('''(e,p)=>{
              const i=e.querySelector('.pin-inner');return e.getBoundingClientRect().top+scrollY-parseFloat(getComputedStyle(i).top)+(e.offsetHeight-i.offsetHeight)*p;
            }''',progress)
            page.evaluate('(y)=>scrollTo({top:y,behavior:"instant"})',y)
            page.wait_for_timeout(150)
            values=page.locator('[data-pin-gallery]').evaluate('''e=>({left:e.querySelector('[data-track]').scrollLeft,max:e.querySelector('[data-track]').scrollWidth-e.querySelector('[data-track]').clientWidth,top:e.querySelector('.pin-inner').getBoundingClientRect().top})''')
            check('desktop pin '+str(progress),abs(values['left']-values['max']*progress)<8,values)
        check('motion toggle removed',page.locator('[data-motion-toggle]').count()==0)
        page.emulate_media(reduced_motion='reduce')
        page.wait_for_function("document.documentElement.classList.contains('motion-paused')")
        check('pause normal flow',page.locator('.pin-inner').evaluate('(e)=>getComputedStyle(e).position')=='relative')
        check('pause reveals all',page.locator('[data-reveal]:not(.is-visible)').count()==0)
        check('pause stops animation',page.locator('.sun-rays').evaluate('(e)=>getComputedStyle(e).animationName')=='none')
        page.emulate_media(reduced_motion='no-preference')
        page.wait_for_function("!document.documentElement.classList.contains('motion-paused')")
        check('system preference restores animation',page.locator('.sun-rays').evaluate('(e)=>getComputedStyle(e).animationName')=='sunspin')
        browser.close()
    (REPORTS/'interaction-audit.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    print(json.dumps({'checks':len(checks),'failures':[c for c in checks if not c['passed']]}))
    assert all(c['passed'] for c in checks)

if __name__=='__main__': run()
