@echo off
title TRADEMON Launcher
cd /d %~dp0

echo =====================================
echo         TRADEMON 起動中...
echo =====================================
echo.

python -m streamlit run home.py

pause