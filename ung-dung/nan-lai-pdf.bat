@echo off
chcp 65001 >nul
cd /d "%~dp0"
python nan_lai_pdf.py %*
pause
