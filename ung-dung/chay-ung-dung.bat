@echo off
chcp 65001 >nul
cd /d "%~dp0"
start "" pythonw giao_dien.py %*
