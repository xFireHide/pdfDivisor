@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

python -m pip install -r requirements-build.txt
if errorlevel 1 exit /b 1

python -m PyInstaller ^
  --onefile ^
  --windowed ^
  --name ProcessadorEtiquetasPDF ^
  --hidden-import=fitz ^
  desktop.py

if errorlevel 1 exit /b 1

echo.
echo Executável gerado: dist\ProcessadorEtiquetasPDF.exe
echo Copie só esse .exe para onde quiser — é portátil (one-file).
pause
