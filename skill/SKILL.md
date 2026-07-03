---
name: draw-local
description: Generate images locally on this laptop's RTX 4060 GPU using ComfyUI + SDXL (no internet or remote server needed). Use whenever the user asks to draw, generate, create, or make a picture/image/illustration/artwork locally (e.g. "고양이 그려줘", "draw a sunset", "로컬로 그려줘"). Auto-starts the ComfyUI server if it is not running.
---

# draw-local

Generate images on the **local** ComfyUI server (SDXL, RTX 4060 Laptop, 8GB VRAM).
Everything runs on this machine — no remote server, no API cost.

## How to generate

Run the bundled script with the user's prompt. Translate non-English prompts to
English for best SDXL results (briefly mention this), but keep proper nouns.

```
C:\ComfyUI\venv\Scripts\python.exe C:\ComfyUI\generate.py "PROMPT HERE"
```

The script auto-starts the ComfyUI server (http://127.0.0.1:8188) if it is not
already running. On success it prints `SAVED <absolute path>` — the PNG on disk.

### Common options
- `--out PATH`   copy the result to a specific path (default stays in `C:\ComfyUI\output\`)
- `--width / --height`  default 1024×1024 (SDXL native — keep near 1024)
- `--steps N`    default 28 (lower = faster)
- `--cfg F`      default 7.0
- `--seed N`     fix to reproduce; omit for a random seed (printed with the result)
- `--negative TEXT`  what to avoid (sensible default)

## REQUIRED final step — show the image to the user

After `SAVED <path>` is printed, **display that PNG inline** (Read the image file)
so the user sees the picture, not just a file path. Then mention the saved path in
one short line.

## Notes
- First image after boot is slower (server start + model load into VRAM, ~1–2 min);
  subsequent ones are ~20–40s on the RTX 4060.
- For variations, call again with a different `--seed`.
- If generation fails with out-of-memory, close other GPU-heavy apps (games, video
  editors) and retry.
