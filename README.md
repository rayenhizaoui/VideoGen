# VideoGen

Générateur de vidéos IA local sur PC (optimisé pour **NVIDIA GeForce RTX 4060 8 GB VRAM**).

---

## 🚀 Modèles Disponibles

| Modèle | Qualité | Vitesse sur RTX 4060 | Recommandation |
| :--- | :---: | :---: | :--- |
| **LTX-Video 2B** | Rapide (Brouillon / Tests) | **~30 à 45 secondes** | Idéal pour tester rapidement des prompts et concepts. |
| **Wan 2.1 14B (GGUF)** | **Cinéma / Photoréaliste** | **~10 à 20 minutes** | Qualité maximale absolue (physique, anatomie, rendu pro). |

---

## 🛠️ Démarrage Rapide

1. **Lancer l'application web simplifiée** :
   Double-cliquez sur :
   👉 `Lancer_VideoGen.bat`
   L'interface s'ouvrira automatiquement sur `http://127.0.0.1:7860`.

2. **Téléchargement des modèles** :
   - Pour les modèles légers **LTX-Video** : double-cliquez sur `download_models.bat`
   - Pour le grand modèle cinéma **Wan 2.1 14B GGUF** : double-cliquez sur `download_wan21_14b.bat`

---

## 📁 Structure du Projet

- `Lancer_VideoGen.bat` : Lanceur 1-clic de l'application web.
- `app.py` : Application web intuitive (Gradio + moteur ComfyUI backend).
- `download_models.bat` / `download_models.ps1` : Téléchargeur LTX-Video.
- `download_wan21_14b.bat` / `download_wan21_14b.ps1` : Téléchargeur Wan 2.1 14B GGUF.
- `ComfyUI_windows_portable/` : Moteur d'inférence autonome avec PyTorch CUDA.
- `output/` : Dossier où toutes vos vidéos générées sont automatiquement enregistrées.
