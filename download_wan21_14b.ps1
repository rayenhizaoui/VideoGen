# Script de telechargement automatique des modeles Wan 2.1 14B GGUF pour ComfyUI
# Optimise pour NVIDIA RTX 4060 (8 GB VRAM) avec RAM Offload

$ErrorActionPreference = "Stop"

$baseDir = $PSScriptRoot
if (Test-Path (Join-Path $baseDir "ComfyUI_windows_portable\ComfyUI\models")) {
    $modelsDir = Join-Path $baseDir "ComfyUI_windows_portable\ComfyUI\models"
} elseif (Test-Path (Join-Path $baseDir "ComfyUI\models")) {
    $modelsDir = Join-Path $baseDir "ComfyUI\models"
} else {
    $modelsDir = Join-Path $baseDir "ComfyUI_windows_portable\ComfyUI\models"
}

$diffusionDir = Join-Path $modelsDir "diffusion_models"
$textEncodersDir = Join-Path $modelsDir "text_encoders"
$vaeDir = Join-Path $modelsDir "vae"
$clipVisionDir = Join-Path $modelsDir "clip_vision"

# Creation des dossiers
@( $diffusionDir, $textEncodersDir, $vaeDir, $clipVisionDir ) | ForEach-Object {
    if (-not (Test-Path $_)) { New-Item -ItemType Directory -Path $_ -Force | Out-Null }
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Telechargement de Wan 2.1 14B (GGUF Quantifie)       " -ForegroundColor Cyan
Write-Host "   Le modele video de qualite cinema pour votre PC       " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. VAE Wan 2.1 (~250 Mo)
$vaeUrl = "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors"
$vaeDest = Join-Path $vaeDir "wan_2.1_vae.safetensors"

Write-Host "[1/4] VAE Wan 2.1 (environ 250 Mo)..." -ForegroundColor Yellow
if ((Test-Path $vaeDest) -and ((Get-Item $vaeDest).Length -gt 250000000)) {
    Write-Host "      -> Deja present et complet !" -ForegroundColor Green
} else {
    & curl.exe -L -C - --retry 5 --retry-delay 3 $vaeUrl -o $vaeDest
}

# 2. CLIP Vision H (~1.25 Go)
$clipUrl = "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors"
$clipDest = Join-Path $clipVisionDir "clip_vision_h.safetensors"

Write-Host ""
Write-Host "[2/4] CLIP Vision H pour l'Image-to-Video (environ 1.25 Go)..." -ForegroundColor Yellow
if ((Test-Path $clipDest) -and ((Get-Item $clipDest).Length -gt 1200000000)) {
    Write-Host "      -> Deja present et complet !" -ForegroundColor Green
} else {
    & curl.exe -L -C - --retry 5 --retry-delay 3 $clipUrl -o $clipDest
}

# 3. Encodeur de texte UMT5 XXL FP8 (~6.7 Go)
$t5Url = "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"
$t5Dest = Join-Path $textEncodersDir "umt5_xxl_fp8_e4m3fn_scaled.safetensors"

Write-Host ""
Write-Host "[3/4] Encodeur de texte UMT5 XXL FP8 (environ 6.7 Go)..." -ForegroundColor Yellow
if ((Test-Path $t5Dest) -and ((Get-Item $t5Dest).Length -gt 6500000000)) {
    Write-Host "      -> Deja present et complet !" -ForegroundColor Green
} else {
    & curl.exe -L -C - --retry 5 --retry-delay 3 $t5Url -o $t5Dest
}

# 4. Modele Wan 2.1 14B Image-to-Video GGUF Q3_K_S (~7.9 Go)
$wanUrl = "https://huggingface.co/city96/Wan2.1-I2V-14B-480P-gguf/resolve/main/wan2.1-i2v-14b-480p-Q3_K_S.gguf"
$wanDest = Join-Path $diffusionDir "wan2.1-i2v-14b-480p-Q3_K_S.gguf"

Write-Host ""
Write-Host "[4/4] Modele principal Wan 2.1 14B I2V (GGUF Q3_K_S, environ 7.9 Go)..." -ForegroundColor Yellow
if ((Test-Path $wanDest) -and ((Get-Item $wanDest).Length -gt 7800000000)) {
    Write-Host "      -> Deja present et complet !" -ForegroundColor Green
} else {
    & curl.exe -L -C - --retry 5 --retry-delay 3 $wanUrl -o $wanDest
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   Wan 2.1 14B GGUF est pret pour des rendus cinema !    " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

