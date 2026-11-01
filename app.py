"""
VideoGen - Generateur de Videos IA Simple
Propulse par LTX-Video (RTX 4060 8GB)
"""

import gradio as gr
import json
import time
import uuid
import os
import sys
import subprocess
import threading
import random
import shutil
import requests
import websocket
from pathlib import Path
from PIL import Image

# ─── Configuration ────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
COMFYUI_DIR = BASE_DIR / "ComfyUI_windows_portable"
COMFYUI_PYTHON = COMFYUI_DIR / "python_embeded" / "python.exe"
COMFYUI_MAIN = COMFYUI_DIR / "ComfyUI" / "main.py"
COMFYUI_INPUT = COMFYUI_DIR / "ComfyUI" / "input"
COMFYUI_OUTPUT = COMFYUI_DIR / "ComfyUI" / "output"
OUTPUT_DIR = BASE_DIR / "output"

SERVER_ADDRESS = "127.0.0.1:8188"
SERVER_URL = f"http://{SERVER_ADDRESS}"

comfyui_process = None

DEFAULT_NEGATIVE = "low quality, worst quality, deformed, distorted, disfigured, motion smear, motion artifacts, fused fingers, bad anatomy, weird hand, ugly"


# ─── ComfyUI Backend ─────────────────────────────────────────────────────────

def start_comfyui_server():
    """Lance le serveur ComfyUI en arriere-plan (invisible)."""
    global comfyui_process

    if comfyui_process is not None:
        try:
            r = requests.get(f"{SERVER_URL}/system_stats", timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            comfyui_process = None

    print("[VideoGen] Demarrage du moteur de generation en arriere-plan...")

    backend_log_path = BASE_DIR / "backend.log"
    backend_log = open(backend_log_path, "a", encoding="utf-8")

    comfyui_process = subprocess.Popen(
        [
            str(COMFYUI_PYTHON), "-s", str(COMFYUI_MAIN),
            "--windows-standalone-build",
            "--lowvram",
            "--preview-method", "auto",
            "--disable-auto-launch",
        ],
        stdout=backend_log,
        stderr=backend_log,
        cwd=str(COMFYUI_DIR),
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )

    # Attendre que le serveur soit pret (max 2 minutes)
    for attempt in range(120):
        try:
            r = requests.get(f"{SERVER_URL}/system_stats", timeout=2)
            if r.status_code == 200:
                print("[VideoGen] Moteur pret !")
                return True
        except Exception:
            pass
        time.sleep(1)

    raise RuntimeError("Le moteur de generation n'a pas demarre dans les 2 minutes.")


def stop_comfyui_server():
    """Arrete le serveur ComfyUI."""
    global comfyui_process
    if comfyui_process is not None:
        comfyui_process.terminate()
        comfyui_process.wait(timeout=10)
        comfyui_process = None


def upload_image_to_comfyui(image_path: str) -> str:
    """Upload une image dans ComfyUI et retourne le nom du fichier."""
    with open(image_path, "rb") as f:
        filename = Path(image_path).name
        files = {"image": (filename, f, "image/png")}
        data = {"overwrite": "true"}
        r = requests.post(f"{SERVER_URL}/upload/image", files=files, data=data)
        r.raise_for_status()
        return r.json()["name"]


def queue_prompt(workflow: dict) -> tuple:
    """Soumet un workflow au serveur ComfyUI."""
    client_id = str(uuid.uuid4())
    r = requests.post(
        f"{SERVER_URL}/prompt",
        json={"prompt": workflow, "client_id": client_id},
    )
    r.raise_for_status()
    result = r.json()
    return result["prompt_id"], client_id


def wait_for_completion(prompt_id: str, client_id: str, progress_callback=None):
    """Attend la fin de la generation via WebSocket."""
    ws = websocket.WebSocket()
    ws.connect(f"ws://{SERVER_ADDRESS}/ws?clientId={client_id}")
    ws.settimeout(600)  # 10 minutes max

    try:
        while True:
            msg = ws.recv()
            if isinstance(msg, str):
                data = json.loads(msg)
                msg_type = data.get("type", "")

                if msg_type == "progress":
                    d = data["data"]
                    current = d.get("value", 0)
                    total = d.get("max", 1)
                    if progress_callback:
                        progress_callback(current / total, f"Etape {current}/{total}")

                elif msg_type == "execution_error":
                    d = data.get("data", {})
                    err_msg = d.get("exception_message", "Erreur inconnue")
                    raise RuntimeError(f"Erreur du moteur de generation: {err_msg}")

                elif msg_type == "executing":
                    d = data["data"]
                    if d.get("node") is None and d.get("prompt_id") == prompt_id:
                        break  # Generation terminee
    finally:
        ws.close()


def get_output_files(prompt_id: str) -> list:
    """Recupere les fichiers de sortie d'une generation."""
    r = requests.get(f"{SERVER_URL}/history/{prompt_id}")
    r.raise_for_status()
    history = r.json()

    if prompt_id not in history:
        return []

    files = []
    outputs = history[prompt_id].get("outputs", {})
    for node_id, node_output in outputs.items():
        # Animated WEBP outputs
        if "images" in node_output:
            for img_info in node_output["images"]:
                files.append(img_info)
        # GIF outputs
        if "gifs" in node_output:
            for gif_info in node_output["gifs"]:
                files.append(gif_info)
    return files


def download_output(file_info: dict, dest_dir: Path) -> Path:
    """Telecharge un fichier de sortie depuis ComfyUI."""
    filename = file_info["filename"]
    subfolder = file_info.get("subfolder", "")
    file_type = file_info.get("type", "output")

    params = {"filename": filename, "type": file_type}
    if subfolder:
        params["subfolder"] = subfolder

    r = requests.get(f"{SERVER_URL}/view", params=params)
    r.raise_for_status()

    dest_dir.mkdir(parents=True, exist_ok=True)
    output_path = dest_dir / filename
    with open(output_path, "wb") as f:
        f.write(r.content)
    return output_path


# ─── Workflows API Format ────────────────────────────────────────────────────

def build_t2v_workflow(prompt: str, width: int, height: int, num_frames: int,
                       steps: int, seed: int) -> dict:
    """Construit le workflow Text-to-Video au format API ComfyUI."""
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "ltx-video-2b-v0.9.5.safetensors"}
        },
        "2": {
            "class_type": "CLIPLoader",
            "inputs": {"clip_name": "t5xxl_fp8_e4m3fn.safetensors", "type": "ltxv", "device": "default"}
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt, "clip": ["2", 0]}
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": DEFAULT_NEGATIVE, "clip": ["2", 0]}
        },
        "5": {
            "class_type": "EmptyLTXVLatentVideo",
            "inputs": {"width": width, "height": height, "length": num_frames, "batch_size": 1}
        },
        "6": {
            "class_type": "LTXVConditioning",
            "inputs": {"positive": ["3", 0], "negative": ["4", 0], "frame_rate": 25}
        },
        "7": {
            "class_type": "LTXVScheduler",
            "inputs": {
                "latent": ["5", 0], "steps": steps,
                "shift": 2.05, "mu": 0.95, "reverse": True, "terminal": 0.1
            }
        },
        "8": {
            "class_type": "KSamplerSelect",
            "inputs": {"sampler_name": "res_multistep"}
        },
        "9": {
            "class_type": "SamplerCustom",
            "inputs": {
                "model": ["1", 0], "add_noise": True, "noise_seed": seed, "cfg": 3.0,
                "positive": ["6", 0], "negative": ["6", 1],
                "sampler": ["8", 0], "sigmas": ["7", 0], "latent_image": ["5", 0],
            }
        },
        "10": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["9", 0], "vae": ["1", 2]}
        },
        "11": {
            "class_type": "SaveAnimatedWEBP",
            "inputs": {
                "images": ["10", 0], "filename_prefix": "VideoGen_T2V",
                "fps": 24, "lossless": False, "quality": 95, "method": "default",
            }
        },
    }


def build_i2v_workflow(image_name: str, prompt: str, width: int, height: int,
                       num_frames: int, steps: int, seed: int) -> dict:
    """Construit le workflow Image-to-Video au format API ComfyUI."""
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "ltx-video-2b-v0.9.5.safetensors"}
        },
        "2": {
            "class_type": "CLIPLoader",
            "inputs": {"clip_name": "t5xxl_fp8_e4m3fn.safetensors", "type": "ltxv", "device": "default"}
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt, "clip": ["2", 0]}
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": DEFAULT_NEGATIVE, "clip": ["2", 0]}
        },
        "5": {
            "class_type": "LoadImage",
            "inputs": {"image": image_name}
        },
        "6": {
            "class_type": "LTXVPreprocess",
            "inputs": {"image": ["5", 0], "target_fps": 40}
        },
        "7": {
            "class_type": "LTXVImgToVideo",
            "inputs": {
                "positive": ["3", 0], "negative": ["4", 0],
                "vae": ["1", 2], "image": ["6", 0],
                "width": width, "height": height, "length": num_frames, "batch_size": 1,
            }
        },
        "8": {
            "class_type": "LTXVConditioning",
            "inputs": {"positive": ["7", 0], "negative": ["7", 1], "frame_rate": 25}
        },
        "9": {
            "class_type": "LTXVScheduler",
            "inputs": {
                "latent": ["7", 2], "steps": steps,
                "shift": 2.05, "mu": 0.95, "reverse": True, "terminal": 0.1,
            }
        },
        "10": {
            "class_type": "KSamplerSelect",
            "inputs": {"sampler_name": "euler"}
        },
        "11": {
            "class_type": "SamplerCustom",
            "inputs": {
                "model": ["1", 0], "add_noise": True, "noise_seed": seed, "cfg": 3.0,
                "positive": ["8", 0], "negative": ["8", 1],
                "sampler": ["10", 0], "sigmas": ["9", 0], "latent_image": ["7", 2],
            }
        },
        "12": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["11", 0], "vae": ["1", 2]}
        },
        "13": {
            "class_type": "SaveAnimatedWEBP",
            "inputs": {
                "images": ["12", 0], "filename_prefix": "VideoGen_I2V",
                "fps": 24, "lossless": False, "quality": 90, "method": "default",
            }
        },
    }


# ─── Generation Functions ────────────────────────────────────────────────────

def generate_text_to_video(prompt, width, height, num_frames, steps, seed, progress=gr.Progress()):
    """Genere une video a partir d'un texte."""
    if not prompt or not prompt.strip():
        raise gr.Error("Veuillez entrer une description de la scene.")

    progress(0, desc="Demarrage du moteur...")
    start_comfyui_server()

    if seed == -1:
        seed = random.randint(0, 2**53)

    progress(0.05, desc="Preparation du workflow...")
    workflow = build_t2v_workflow(prompt, width, height, num_frames, steps, seed)

    progress(0.1, desc="Envoi au moteur de generation...")
    prompt_id, client_id = queue_prompt(workflow)

    def on_progress(pct, msg):
        progress(0.1 + pct * 0.8, desc=msg)

    wait_for_completion(prompt_id, client_id, on_progress)

    progress(0.95, desc="Recuperation de la video...")
    files = get_output_files(prompt_id)
    if not files:
        raise gr.Error("Aucune video generee. Verifiez les logs du moteur.")

    output_path = download_output(files[0], OUTPUT_DIR)
    progress(1.0, desc="Termine !")
    return str(output_path)


def generate_image_to_video(image, prompt, width, height, num_frames, steps, seed,
                            progress=gr.Progress()):
    """Genere une video a partir d'une image et d'un texte."""
    if image is None:
        raise gr.Error("Veuillez charger une image.")
    if not prompt or not prompt.strip():
        raise gr.Error("Veuillez entrer une description du mouvement souhaite.")

    progress(0, desc="Demarrage du moteur...")
    start_comfyui_server()

    if seed == -1:
        seed = random.randint(0, 2**53)

    # Sauvegarder l'image temporairement pour l'upload
    progress(0.05, desc="Envoi de l'image au moteur...")
    temp_path = BASE_DIR / "temp_input.png"
    if isinstance(image, str):
        shutil.copy(image, temp_path)
    else:
        Image.fromarray(image).save(temp_path)

    image_name = upload_image_to_comfyui(str(temp_path))
    temp_path.unlink(missing_ok=True)

    progress(0.1, desc="Preparation du workflow...")
    workflow = build_i2v_workflow(image_name, prompt, width, height, num_frames, steps, seed)

    progress(0.15, desc="Generation en cours...")
    prompt_id, client_id = queue_prompt(workflow)

    def on_progress(pct, msg):
        progress(0.15 + pct * 0.75, desc=msg)

    wait_for_completion(prompt_id, client_id, on_progress)

    progress(0.95, desc="Recuperation de la video...")
    files = get_output_files(prompt_id)
    if not files:
        raise gr.Error("Aucune video generee. Verifiez les logs du moteur.")

    output_path = download_output(files[0], OUTPUT_DIR)
    progress(1.0, desc="Termine !")
    return str(output_path)


# ─── Interface Utilisateur ────────────────────────────────────────────────────

CSS = """
.main-title {
    text-align: center;
    margin-bottom: 0.5em;
}
.subtitle {
    text-align: center;
    color: #666;
    font-size: 0.95em;
    margin-bottom: 1.5em;
}
footer { display: none !important; }
"""

def create_app():
    with gr.Blocks(
        theme=gr.themes.Soft(primary_hue="blue", secondary_hue="slate"),
        title="VideoGen - Generateur de Videos IA",
        css=CSS,
    ) as app:

        gr.HTML('<h1 class="main-title">🎬 VideoGen</h1>')
        gr.HTML('<p class="subtitle">Generateur de videos IA local &bull; RTX 4060 &bull; LTX-Video</p>')

        with gr.Tabs():

            # ── Tab 1 : Image → Video ─────────────────────────────────────
            with gr.Tab("🖼️ Image → Video", id="i2v"):
                gr.Markdown("Chargez une image et decrivez le mouvement souhaite.")

                with gr.Row():
                    with gr.Column(scale=1):
                        i2v_image = gr.Image(
                            label="Image source",
                            type="numpy",
                            height=300,
                        )
                        i2v_prompt = gr.Textbox(
                            label="Description du mouvement",
                            placeholder="Ex: The camera slowly moves forward, hair blowing gently in the wind, cinematic soft lighting...",
                            lines=3,
                        )
                        with gr.Accordion("Reglages avances", open=False):
                            with gr.Row():
                                i2v_width = gr.Slider(256, 1024, value=768, step=32, label="Largeur")
                                i2v_height = gr.Slider(256, 1024, value=512, step=32, label="Hauteur")
                            with gr.Row():
                                i2v_frames = gr.Slider(17, 161, value=97, step=8, label="Nombre de frames")
                                i2v_steps = gr.Slider(10, 50, value=30, step=1, label="Etapes de generation")
                            i2v_seed = gr.Number(label="Seed (-1 = aleatoire)", value=-1, precision=0)

                        i2v_btn = gr.Button("🎬 Generer la Video", variant="primary", size="lg")

                    with gr.Column(scale=1):
                        i2v_output = gr.Image(label="Video generee", height=400)
                        i2v_download = gr.File(label="Telecharger")

                i2v_btn.click(
                    fn=generate_image_to_video,
                    inputs=[i2v_image, i2v_prompt, i2v_width, i2v_height,
                            i2v_frames, i2v_steps, i2v_seed],
                    outputs=[i2v_output],
                ).then(
                    fn=lambda x: x,
                    inputs=[i2v_output],
                    outputs=[i2v_download],
                )

            # ── Tab 2 : Texte → Video ─────────────────────────────────────
            with gr.Tab("📝 Texte → Video", id="t2v"):
                gr.Markdown("Decrivez la scene en detail pour obtenir les meilleurs resultats.")

                with gr.Row():
                    with gr.Column(scale=1):
                        t2v_prompt = gr.Textbox(
                            label="Description de la scene",
                            placeholder="Ex: A cinematic shot of a sports car driving through a neon-lit city at night, rain reflections on the road, smooth tracking camera...",
                            lines=5,
                        )
                        with gr.Accordion("Reglages avances", open=False):
                            with gr.Row():
                                t2v_width = gr.Slider(256, 1024, value=768, step=32, label="Largeur")
                                t2v_height = gr.Slider(256, 1024, value=512, step=32, label="Hauteur")
                            with gr.Row():
                                t2v_frames = gr.Slider(17, 161, value=97, step=8, label="Nombre de frames")
                                t2v_steps = gr.Slider(10, 50, value=30, step=1, label="Etapes de generation")
                            t2v_seed = gr.Number(label="Seed (-1 = aleatoire)", value=-1, precision=0)

                        t2v_btn = gr.Button("🎬 Generer la Video", variant="primary", size="lg")

                    with gr.Column(scale=1):
                        t2v_output = gr.Image(label="Video generee", height=400)
                        t2v_download = gr.File(label="Telecharger")

                t2v_btn.click(
                    fn=generate_text_to_video,
                    inputs=[t2v_prompt, t2v_width, t2v_height,
                            t2v_frames, t2v_steps, t2v_seed],
                    outputs=[t2v_output],
                ).then(
                    fn=lambda x: x,
                    inputs=[t2v_output],
                    outputs=[t2v_download],
                )

        gr.Markdown(
            "---\n"
            "💡 **Conseils** : Utilisez des descriptions longues et detaillees (sujet, decor, eclairage, mouvement de camera). "
            "Resolution recommandee : 768×512. La premiere generation peut prendre 1-2 min (chargement du modele)."
        )

    return app


# ─── Point d'entree ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 56)
    print("  🎬 VideoGen - Generateur de Videos IA Local")
    print("  Optimise pour RTX 4060 (8 GB VRAM)")
    print("=" * 56)
    print()

    try:
        # Prechauffage du moteur en arriere-plan
        threading.Thread(target=start_comfyui_server, daemon=True).start()
        app = create_app()
        app.launch(
            server_name="127.0.0.1",
            server_port=7860,
            inbrowser=True,
            share=False,
            show_error=True,
        )
    finally:
        stop_comfyui_server()

