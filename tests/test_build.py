"""Regressions for bilingual build encoding and environment-specific indexing."""
import json
import os
import re
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class BuildEncodingTest(unittest.TestCase):
    def test_build_with_ascii_default_preserves_chinese_html(self):
        # Simulate a non-UTF-8 locale on any OS, including modern UTF-8 Windows.
        script = """
import io, runpy
original_open = io.open
def locale_open(file, mode='r', buffering=-1, encoding=None, *args, **kwargs):
    if 'b' not in mode and encoding in (None, 'locale'):
        encoding = 'ascii'
    return original_open(file, mode, buffering, encoding, *args, **kwargs)
io.open = locale_open
runpy.run_path('build.py', run_name='__main__')
"""
        result = subprocess.run([sys.executable, '-c', script], cwd=ROOT,
                                capture_output=True, env=os.environ)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace'))
        self.assertIn('黄金海岸', (ROOT / 'dist/zh/index.html').read_text(encoding='utf-8'))
        self.assertEqual(len(list((ROOT / 'dist').rglob('*.html'))), 69)


    def test_production_metadata_and_sitemap_are_isolated_from_preview(self):
        dist = ROOT / 'dist'
        preview_robots = (dist / 'robots.txt').read_bytes()
        preview_home = (dist / 'index.html').read_bytes()
        artifacts = ROOT / 'artifacts'
        artifacts.mkdir(exist_ok=True)
        origin = 'https://goldcoastcommercialrepairs.com.au'
        with TemporaryDirectory(dir=artifacts) as scratch:
            output = Path(scratch) / 'production'
            result = subprocess.run(
                [sys.executable, 'build.py', '--production-dir', str(output)],
                cwd=ROOT, capture_output=True, encoding='utf-8',
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            namespace = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
            locations = [
                loc.text for loc in ET.parse(output / 'sitemap.xml').iter(f'{namespace}loc')
            ]
            expected = set()
            for page in output.rglob('index.html'):
                parts = page.relative_to(output).parent.parts
                route = '/' + '/'.join(parts) + '/' if parts else '/'
                en_parts = parts[1:] if parts and parts[0] == 'zh' else parts
                en_route = '/' + '/'.join(en_parts) + '/' if en_parts else '/'
                canonical = origin + route
                expected.add(canonical)
                html = page.read_text(encoding='utf-8')
                self.assertIn(f'<link rel="canonical" href="{canonical}">', html)
                self.assertIn(f'hreflang="en-AU" href="{origin + en_route}"', html)
                self.assertIn(f'hreflang="zh-CN" href="{origin + "/zh" + en_route}"', html)
                self.assertIn(f'hreflang="x-default" href="{origin + en_route}"', html)
                self.assertIn(f'property="og:image" content="{origin}/assets/', html)
                self.assertNotIn('<meta name="robots"', html)
                match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html)
                if en_route == '/':
                    self.assertIsNone(match)
                    self.assertNotIn('class="site-breadcrumbs"', html)
                else:
                    self.assertIsNotNone(match)
                    schema = json.loads(match.group(1))
                    self.assertEqual(schema['@type'], 'BreadcrumbList')
                    crumbs = schema['itemListElement']
                    self.assertEqual([item['position'] for item in crumbs], list(range(1, len(crumbs) + 1)))
                    prefix = '/zh' if route.startswith('/zh/') else ''
                    urls = [origin + prefix + '/']
                    if len(en_parts) > 1:
                        urls.append(origin + prefix + '/' + en_parts[0] + '/')
                    self.assertEqual([item['item'] for item in crumbs], urls + [canonical])
                    self.assertIn('<li aria-current="page">', html)
                preview_html = (dist / page.relative_to(output)).read_text(encoding='utf-8')
                self.assertEqual(html.split('</head>', 1)[1], preview_html.split('</head>', 1)[1])
            self.assertEqual(len(expected), 68)
            self.assertEqual(locations, sorted(expected))
            self.assertEqual(
                (output / 'robots.txt').read_text(encoding='utf-8'),
                f'User-agent: *\nDisallow:\nSitemap: {origin}/sitemap.xml\n',
            )
            self.assertIn('content="noindex"', (output / '404.html').read_text(encoding='utf-8'))
            self.assertEqual(
                (output / '404.html').read_bytes(), (dist / '404.html').read_bytes(),
            )
            for name in ('style.css', 'gc-inner-v4.js', 'assets/coast-hero.webp'):
                self.assertEqual((output / name).read_bytes(), (dist / name).read_bytes())
        self.assertEqual((dist / 'robots.txt').read_bytes(), preview_robots)
        self.assertEqual((dist / 'index.html').read_bytes(), preview_home)
        self.assertFalse((dist / 'sitemap.xml').exists())


if __name__ == '__main__':
    unittest.main()
