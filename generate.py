"""Generate an image on the local ComfyUI server (SDXL, RTX 4060).

Usage:
    python generate.py "PROMPT" [--out PATH] [--width N] [--height N]
                       [--steps N] [--cfg F] [--seed N] [--negative TEXT]

Auto-starts the ComfyUI server if it is not already running.
Prints `SAVED <absolute path>` on success.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

COMFY_DIR = r"C:\ComfyUI"
PYTHON = os.path.join(COMFY_DIR, "venv", "Scripts", "python.exe")
SERVER = "http://127.0.0.1:8188"


def server_alive():
    try:
        urllib.request.urlopen(SERVER + "/system_stats", timeout=2)
        return True
    except Exception:
        return False


def ensure_server():
    if server_alive():
        return
    print("starting ComfyUI server...", flush=True)
    flags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
    subprocess.Popen(
        [PYTHON, os.path.join(COMFY_DIR, "main.py"), "--port", "8188"],
        cwd=COMFY_DIR, creationflags=flags,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    for _ in range(60):
        time.sleep(2)
        if server_alive():
            return
    sys.exit("ERROR: ComfyUI server did not come up within 120s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("--out", default=None)
    ap.add_argument("--width", type=int, default=1024)
    ap.add_argument("--height", type=int, default=1024)
    ap.add_argument("--steps", type=int, default=28)
    ap.add_argument("--cfg", type=float, default=7.0)
    ap.add_argument("--seed", type=int, default=-1)
    ap.add_argument("--negative", default="blurry, low quality, distorted, watermark, text, deformed")
    args = ap.parse_args()

    seed = args.seed if args.seed >= 0 else int.from_bytes(os.urandom(4), "big")

    ensure_server()

    workflow = {
        "4": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
        "5": {"class_type": "EmptyLatentImage",
              "inputs": {"width": args.width, "height": args.height, "batch_size": 1}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": args.prompt, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": args.negative, "clip": ["4", 1]}},
        "3": {"class_type": "KSampler",
              "inputs": {"seed": seed, "steps": args.steps, "cfg": args.cfg,
                         "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0,
                         "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0],
                         "latent_image": ["5", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "claude"}},
    }

    req = urllib.request.Request(SERVER + "/prompt",
                                 data=json.dumps({"prompt": workflow}).encode(),
                                 headers={"Content-Type": "application/json"})
    pid = json.loads(urllib.request.urlopen(req).read())["prompt_id"]

    t0 = time.time()
    while True:
        time.sleep(2)
        hist = json.loads(urllib.request.urlopen(SERVER + "/history/" + pid).read())
        if pid in hist:
            entry = hist[pid]
            if entry.get("status", {}).get("status_str") == "error":
                sys.exit("ERROR: " + json.dumps(entry["status"])[:2000])
            images = [img for node in entry.get("outputs", {}).values()
                      for img in node.get("images", [])]
            if images:
                img = images[0]
                sub = img.get("subfolder", "")
                path = os.path.join(COMFY_DIR, "output", sub, img["filename"])
                if args.out:
                    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
                    import shutil
                    shutil.copy2(path, args.out)
                    path = os.path.abspath(args.out)
                print(f"SAVED {path}  (seed {seed}, {time.time() - t0:.0f}s)")
                return
        if time.time() - t0 > 540:
            sys.exit("ERROR: timed out waiting for generation")


if __name__ == "__main__":
    main()
