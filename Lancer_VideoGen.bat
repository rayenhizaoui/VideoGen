@echo off
title VideoGen - Generateur de Videos IA
echo ========================================================
echo   Lancement de VideoGen (Interface Simple)
echo   Optimise pour NVIDIA RTX 4060 (8 GB VRAM)
echo ========================================================
echo.
echo Demarrage du serveur et ouverture automatique de votre navigateur...
echo (Laissez cette fenetre ouverte pendant l'utilisation)
echo.

cd /d "%~dp0"
.\ComfyUI_windows_portable\python_embeded\python.exe app.py
pause
