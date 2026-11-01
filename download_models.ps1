# Script de telechargement automatique des modeles LTX-Video pour ComfyUI
# Optimise pour GPU 8 GB VRAM (RTX 4060)

$ErrorActionPreference = "Stop"

$baseDir = $PSScriptRoot
if (Test-Path (Join-Path $baseDir "ComfyUI_windows_portable\ComfyUI\models")) {
    $modelsDir = Join-Path $baseDir "ComfyUI_windows_portable\ComfyUI\models"
} elseif (Test-Path (Join-Path $baseDir "ComfyUI\models")) {
    $modelsDir = Join-Path $baseDir "ComfyUI\models"
} else {
    $modelsDir = Join-Path $baseDir "ComfyUI_windows_portable\ComfyUI\models"
}
$checkpointsDir = Join-Path $modelsDir "checkpoints"
$textEncodersDir = Join-Path $modelsDir "text_encoders"

# Creation des dossiers si necessaire
if (-not (Test-Path $checkpointsDir)) { New-Item -ItemType Directory -Path $checkpointsDir -Force | Out-Null }
if (-not (Test-Path $textEncodersDir)) { New-Item -ItemType Directory -Path $textEncodersDir -Force | Out-Null }

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Telechargement des Modeles LTX-Video pour ComfyUI     " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Modele Checkpoint LTX-Video 0.9.5
$ltxUrl = "https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltx-video-2b-v0.9.5.safetensors"
$ltxDest = Join-Path $checkpointsDir "ltx-video-2b-v0.9.5.safetensors"

Write-Host "[1/2] Verification du modele LTX-Video 2B (v0.9.5)..." -ForegroundColor Yellow
if (Test-Path $ltxDest) {
    $size = (Get-Item $ltxDest).Length
    if ($size -gt 6000000000) {
        Write-Host "      -> Deja present et complet ($([math]::Round($size / 1GB, 2)) GB) !" -ForegroundColor Green
    } else {
        Write-Host "      -> Fichier partiel detecte, reprise du telechargement..." -ForegroundColor Magenta
        & curl.exe -L -C - --retry 5 --retry-delay 3 $ltxUrl -o $ltxDest
    }
} else {
    Write-Host "      -> Telechargement en cours (environ 6.3 GB)..." -ForegroundColor White
    & curl.exe -L -C - --retry 5 --retry-delay 3 $ltxUrl -o $ltxDest
}

# 2. Text Encoder T5 XXL FP8
$t5Url = "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors"
$t5Dest = Join-Path $textEncodersDir "t5xxl_fp8_e4m3fn.safetensors"

Write-Host ""
Write-Host "[2/2] Verification de l'encodeur de texte T5 XXL (FP8 optimise 8GB)..." -ForegroundColor Yellow
if (Test-Path $t5Dest) {
    $size = (Get-Item $t5Dest).Length
    if ($size -gt 4500000000) {
        Write-Host "      -> Deja present et complet ($([math]::Round($size / 1GB, 2)) GB) !" -ForegroundColor Green
    } else {
        Write-Host "      -> Fichier partiel detecte, reprise du telechargement..." -ForegroundColor Magenta
        & curl.exe -L -C - --retry 5 --retry-delay 3 $t5Url -o $t5Dest
    }
} else {
    Write-Host "      -> Telechargement en cours (environ 4.9 GB)..." -ForegroundColor White
    & curl.exe -L -C - --retry 5 --retry-delay 3 $t5Url -o $t5Dest
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   Tous les modeles LTX-Video sont prets a l'emploi !     " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
