@echo off
setlocal
cd /d "%~dp0"
echo Gold Coast website preview
echo Open http://127.0.0.1:8000/ or http://127.0.0.1:8000/zh/
echo Press Ctrl+C to stop the local preview.
where py >nul 2>nul
if not errorlevel 1 (
  py -3 -m http.server 8000 --bind 127.0.0.1 --directory dist
  goto done
)
where python >nul 2>nul
if not errorlevel 1 (
  python -m http.server 8000 --bind 127.0.0.1 --directory dist
  goto done
)
echo Python 3 was not found. Open this folder in Codex and use CODEX_PROMPT.txt.
:done
pause
