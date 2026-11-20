"""Regression: Windows non-UTF-8 defaults must not break bilingual builds."""
import os
from pathlib import Path
import subprocess
import sys
import unittest

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


if __name__ == '__main__':
    unittest.main()
