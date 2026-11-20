"""Local representative viewport audit; screenshots and measurements in reports."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT.parent / 'reports'
BASE = 'http://127.0.0.1:8765'
CHROME = 'C:/Users/UFTR/AppData/Local/ms-playwright/chromium-1234/chrome-win64/chrome.exe'

def run():
    shots = REPORTS / 'screenshots'
    shots.mkdir(exist_ok=True)
    records, errors = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, headless=True)
        page = browser.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        data = json.loads((ROOT / 'src/content.json').read_text(encoding='utf-8'))
        routes = ['/', '/services/', '/sectors/', '/news/', '/faq/', '/contact/',
                  '/services/'+data['services'][0]['slug']+'/',
                  '/sectors/'+data['sectors'][0]['slug']+'/',
                  '/news/'+data['articles'][0]['slug']+'/']
        for width in [375, 390, 768, 1440]:
            page.set_viewport_size({'width': width, 'height': 960 if width > 768 else 844})
            for lang in ['', '/zh']:
                for route in routes:
                    response = page.goto(BASE+lang+route)
                    page.evaluate('document.fonts.ready')
                    page.wait_for_timeout(120)
                    record = page.evaluate('''() => ({
                      width: innerWidth, pageWidth: document.documentElement.scrollWidth,
                      nav: document.querySelectorAll('#primary-nav>a').length,
                      h1: document.querySelector('h1')?.textContent,
                      font: getComputedStyle(document.querySelector('h1')).fontFamily,
                      overflow: [...document.querySelectorAll('h1,h2,h3,.button,input,select,textarea')]
                        .filter(e=>!e.closest('[data-track]') && e.getBoundingClientRect().width &&
                          (e.getBoundingClientRect().right>innerWidth+2 || e.getBoundingClientRect().left < -2))
                        .map(e=>({tag:e.tagName, text:e.textContent.slice(0,80), x:e.getBoundingClientRect().x, width:e.getBoundingClientRect().width}))
                    })''')
                    record.update(route=lang+route, status=response.status)
                    records.append(record)
                    if (width == 1440 and lang == '' and route in routes[:4]) or (width == 390 and route == '/'):
                        page.wait_for_timeout(1400)
                        name = ('zh-' if lang else 'en-')+('home' if route=='/' else route.strip('/'))+'-'+str(width)
                        page.screenshot(path=str(shots/(name+'.png')))
        browser.close()
    result = {'views':records,'page_errors':errors}
    (REPORTS/'browser-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'views':len(records),'page_errors':errors,'overflow':[r for r in records if r['pageWidth']>r['width'] or r['overflow']]},ensure_ascii=True))

if __name__ == '__main__':
    run()
