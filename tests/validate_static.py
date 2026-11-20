"""Validate generated routes, metadata, internal links and local resources."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.refs, self.ids, self.styles, self.scripts, self.alternates = [], set(), [], [], []
        self.h1, self.noindex, self.nav, self.in_nav = 0, False, 0, False
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'): self.ids.add(a['id'])
        if tag == 'h1': self.h1 += 1
        if tag == 'nav' and a.get('id') == 'primary-nav': self.in_nav = True
        if tag == 'a' and self.in_nav: self.nav += 1
        if tag == 'meta' and a.get('name') == 'robots': self.noindex = 'noindex' in a.get('content','')
        if tag == 'link' and a.get('rel') == 'alternate': self.alternates.append(a)
        if tag == 'link' and a.get('rel') == 'stylesheet': self.styles.append(a['href'])
        if tag == 'script': self.scripts.append(a)
        for k in ['href','src']:
            if a.get(k): self.refs.append(a[k])
    def handle_endtag(self, tag):
        if tag == 'nav': self.in_nav = False

def run():
    pages = {p: Page(p.read_text(encoding='utf-8')) for p in DIST.rglob('*.html')}
    errors, links, resources = [], 0, 0
    def target(path):
        return path/'index.html' if path.is_dir() else path
    for path,page in pages.items():
        rel=path.relative_to(DIST).as_posix()
        if page.h1 != 1 or not page.noindex: errors.append(f'{rel}: H1/noindex')
        if rel != '404.html':
            if page.nav != 7: errors.append(f'{rel}: navigation {page.nav}')
            if page.styles != ['/style.css','/surf-font.css','/chinese-font.css','/maximal.css','/interiors.css']: errors.append(f'{rel}: CSS order')
            if [s.get('src') for s in page.scripts] != ['/app.js','/motion.js'] or not all('defer' in s for s in page.scripts): errors.append(f'{rel}: scripts')
            if len(page.alternates)!=2: errors.append(f'{rel}: language alternates')
            for a in page.alternates:
                if not target(DIST/urlsplit(a['href']).path.lstrip('/')).is_file(): errors.append(f'{rel}: alternate missing')
        for ref in page.refs:
            u=urlsplit(ref)
            if u.scheme or u.netloc: continue
            dest=target((DIST/u.path.lstrip('/')) if u.path.startswith('/') else (path.parent/u.path if u.path else path))
            if not dest.is_file(): errors.append(f'{rel}: missing {ref}')
            elif u.fragment and dest in pages and unquote(u.fragment) not in pages[dest].ids: errors.append(f'{rel}: missing anchor {ref}')
            if dest.suffix=='.html': links+=1
            else: resources+=1
    for css in DIST.glob('*.css'):
        for ref in re.findall(r'url\([\'"]?([^\)\'"\s]+)',css.read_text(encoding='utf-8')):
            if ref.startswith(('data:','http')): continue
            dest=DIST/ref.lstrip('/') if ref.startswith('/') else css.parent/ref
            if not dest.is_file(): errors.append(f'{css.name}: missing {ref}')
    assert (DIST/'robots.txt').read_text(encoding='utf-8')=='User-agent: *\nDisallow: /\n'
    result={'html_pages':len(pages),'language_pairs':(len(pages)-1)//2,'internal_links':links,'local_references':resources,'errors':errors}
    (ROOT.parent/'reports/static-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result))
    if errors: raise SystemExit(1)

if __name__=='__main__': run()
