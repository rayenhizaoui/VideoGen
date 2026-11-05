@echo off
title Telechargement Wan 2.1 14B GGUF
echo ========================================================
echo   Telechargement des modeles Wan 2.1 14B (GGUF)
echo ========================================================
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0download_wan21_14b.ps1"
pause
