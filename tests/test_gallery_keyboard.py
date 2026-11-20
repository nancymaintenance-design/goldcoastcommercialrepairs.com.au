"""Regression: galleries must expose a stable keyboard scroll target."""
import unittest
from playwright.sync_api import sync_playwright
from browser_audit import BASE, CHROME

class GalleryKeyboardTest(unittest.TestCase):
    def test_both_tracks_accept_focus_and_native_arrow_scroll(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=CHROME, headless=True)
            page = browser.new_page(viewport={'width':390, 'height':844}, reduced_motion='reduce')
            page.goto(BASE+'/')
            for selector in ['.sector-section', '.news-section']:
                with self.subTest(gallery=selector):
                    track = page.locator(selector+' [data-track]')
                    track.focus()
                    self.assertTrue(track.evaluate('(e)=>document.activeElement===e'))
                    page.keyboard.press('ArrowRight')
                    page.wait_for_timeout(250)
                    self.assertGreater(track.evaluate('(e)=>e.scrollLeft'), 0)
            browser.close()

if __name__=='__main__': unittest.main()
