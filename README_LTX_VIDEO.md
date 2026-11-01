# Guide LTX-Video & ComfyUI (Optimise RTX 4060 8GB)

Ce dossier contient l'environnement complet pour generer des videos par IA en local sur votre PC avec votre carte graphique **NVIDIA GeForce RTX 4060 (8 GB VRAM)**.

---

## 1. Structure du dossier

- **`ComfyUI_windows_portable/`** : L'environnement autonome ComfyUI avec Python integre et PyTorch CUDA preconfigure.
- **`start_comfyui_rtx4060.bat`** : Lanceur 1-clic avec optimisation memoire (`--lowvram`) speciale pour 8 GB VRAM.
- **`download_models.ps1`** : Script PowerShell pour telecharger automatiquement les poids des modeles (avec reprise en cas de coupure).
- **`ltxv_text_to_video.json`** : Workflow preconfigure pour creer une video a partir d'un texte (Text-to-Video).
- **`ltxv_image_to_video.json`** : Workflow preconfigure pour animer une image fixe (Image-to-Video).

---

## 2. Demarrage rapide

### Etape 1 : Finaliser le telechargement des modeles
Si les modeles ne sont pas encore tous telecharges, faites un clic droit sur `download_models.ps1` et choisissez **Executer avec PowerShell** (ou lancez-le dans un terminal PowerShell) :
```powershell
.\download_models.ps1
```
Les fichiers suivants seront places aux bons endroits :
- `ComfyUI\models\checkpoints\ltx-video-2b-v0.9.5.safetensors` (~6.3 GB) : Le modele principal LTX-Video.
- `ComfyUI\models\text_encoders\t5xxl_fp8_e4m3fn.safetensors` (~4.9 GB) : L'encodeur de texte optimise en FP8 (indispensable pour ne pas saturer 8 GB de VRAM).

### Etape 2 : Lancer ComfyUI
Double-cliquez sur **`start_comfyui_rtx4060.bat`**.
Votre navigateur web s'ouvrira automatiquement sur l'interface : `http://127.0.0.1:8188`.

---

## 3. Generer une premiere video (Text-to-Video)

1. Ouvrez l'interface ComfyUI dans votre navigateur.
2. Glissez-deposez le fichier **`ltxv_text_to_video.json`** directement sur la fenetre de ComfyUI (ou cliquez sur le bouton **Load** dans le panneau lateral droit et selectionnez ce fichier).
3. Dans la boite verte **CLIP Text Encode (Positive Prompt)**, tapez une description detaillee de la scene.
   - *Exemple* :  
     `"A cinematic shot of a sleek sports car driving through a neon-lit futuristic city at night, rain-slicked asphalt reflecting vibrant signs, smooth tracking camera movement, photorealistic, 4k"`
4. Cliquez sur le bouton **Queue Prompt** (ou appuyez sur `Ctrl + Entree`).
5. La generation demarre ! En 30 a 60 secondes environ, votre video animee s'affiche dans le panneau d'apercu et est automatiquement enregistree dans `ComfyUI\output\`.

---

## 4. Animer une image fixe (Image-to-Video)

1. Glissez-deposez le fichier **`ltxv_image_to_video.json`** dans ComfyUI.
2. Dans le bloc **Load Image**, chargez votre image source (photo, illustration, portrait, paysage).
3. Dans le prompt positif, decrivez le mouvement souhaite (ex : `"The camera slowly glides forward, hair blowing gently in the wind, cinematic soft light"`).
4. Cliquez sur **Queue Prompt**.

---

## 5. Recommandations et reglages pour RTX 4060 (8 GB VRAM)

| Parametre | Valeur recommandee | Commentaire |
| :--- | :--- | :--- |
| **Resolution** | 768 × 512 ou 720 × 480 | Rapport qualite/vitesse ideal pour 8 GB de VRAM. |
| **Nombre de frames** | 97 a 121 frames | Correspond a 4 a 5 secondes de video fluide (a 24 fps). |
| **Etapes (Steps)** | 25 a 30 steps | Donne une excellente qualite sans ralentir la generation. |
| **Encodeur de texte** | `t5xxl_fp8_e4m3fn` | Version 8-bit allegre qui preserve 4 GB de VRAM supplementaires par rapport a la version FP16. |
| **Style de prompt** | Long et descriptif | LTX-Video reagit beaucoup mieux aux descriptions riches incluant sujet, decors, eclairage et mouvements de camera. |

