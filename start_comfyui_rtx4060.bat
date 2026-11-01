@echo off
title ComfyUI - LTX Video (Optimise RTX 4060 8GB)
echo ========================================================
echo   Lancement de ComfyUI avec optimisation RTX 4060 8GB
echo ========================================================
echo.

set "PY_EXE=.\python_embeded\python.exe"
set "COMFY_MAIN=.\ComfyUI\main.py"

if not exist "%PY_EXE%" (
    if exist ".\ComfyUI_windows_portable\python_embeded\python.exe" (
        cd /d ".\ComfyUI_windows_portable"
    ) else (
        echo [ERREUR] python_embeded introuvable.
        echo Verifiez que le telechargement et l'extraction sont termines.
        pause
        exit /b 1
    )
)

echo Demarrage de ComfyUI en mode lowvram pour gerer efficacement la VRAM...
.\python_embeded\python.exe -s .\ComfyUI\main.py --windows-standalone-build --lowvram --preview-method auto %*
pause
