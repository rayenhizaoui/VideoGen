# VideoGen

Environnement local pour la génération de vidéos par IA sur PC (optimisé pour **NVIDIA RTX 4060 / 4060 Ti 8 GB VRAM**).

Ce dépôt contient les scripts d'automatisation et les workflows **ComfyUI** prêts à l'emploi pour le modèle **LTX-Video**.

## Contenu du dépôt
- `ltxv_text_to_video.json` : Workflow ComfyUI pour le Text-to-Video.
- `ltxv_image_to_video.json` : Workflow ComfyUI pour l'Image-to-Video.
- `start_comfyui_rtx4060.bat` : Lanceur 1-clic avec optimisation VRAM (`--lowvram`).
- `download_models.ps1` / `download_models.bat` : Téléchargement automatique des modèles (LTX-Video 2B et T5 XXL FP8).
- `README_LTX_VIDEO.md` : Guide pas à pas détaillé pour la configuration et la génération.

