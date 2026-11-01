@echo off
title Telechargement des modeles LTX-Video
echo Lancement du script PowerShell de telechargement...
powershell -ExecutionPolicy Bypass -File "%~dp0download_models.ps1"
pause
