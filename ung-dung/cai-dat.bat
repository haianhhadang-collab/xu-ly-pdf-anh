@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Cai thu vien Python can thiet...
python -m pip install -r requirements.txt
echo.
echo Kiem tra Tesseract OCR:
tesseract --list-langs
if errorlevel 1 echo Chua co Tesseract. Tai tai https://github.com/UB-Mannheim/tesseract/wiki va chon them goi Vietnamese.
pause
