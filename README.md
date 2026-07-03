# claude-comfyui-local

**클로드(Claude)가 내 PC의 GPU로 직접 그림을 그리게 만들기** — ComfyUI + SDXL 로컬 연동 가이드
*Make Claude generate images on your own local GPU via ComfyUI + SDXL (free, offline, no API cost).*

"고양이 그려줘" 한마디면 클로드가 프롬프트를 영어로 다듬고, 로컬 ComfyUI 서버를 자동 기동해서, 완성된 그림을 채팅에 보여준다. 비용 0원, 인터넷 불필요.

> 상세한 설치기는 블로그 글 참고: [클로드가 내 노트북에서 직접 그림을 그리게 만들기](https://junstellar.github.io/p/claude-local-image-generation/)

## 동작 구조

```
사용자: "노을 지는 서울 야경 그려줘"
   ↓
클로드: 한국어 요청 → 영어 프롬프트로 변환·보강
   ↓
ComfyUI 서버 (로컬, http://127.0.0.1:8188) ← 꺼져 있으면 자동 기동
   ↓
SDXL 모델이 GPU에서 이미지 생성 (RTX 4060 기준 20~40초)
   ↓
클로드가 완성된 PNG를 채팅에 표시
```

## 요구 사양

| 항목 | 필요 사양 | 비고 |
|---|---|---|
| GPU VRAM | 8GB 이상 권장 | SDXL 기준. 6GB 이하면 SD 1.5 권장 |
| RAM | 16GB | |
| 디스크 | 약 20GB | ComfyUI + PyTorch + SDXL 모델 |
| SW | Python 3.10~3.12, git | Windows 11에서 검증 |

## 설치 (Windows 기준)

```powershell
# 1. ComfyUI 클론 + 가상환경
git clone --depth 1 https://github.com/comfyanonymous/ComfyUI C:\ComfyUI
python -m venv C:\ComfyUI\venv

# 2. PyTorch (CUDA) — 반드시 CUDA 인덱스 지정 (기본 pip는 CPU 버전!)
C:\ComfyUI\venv\Scripts\python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# 3. 의존성 + SDXL 모델 (~6.5GB)
C:\ComfyUI\venv\Scripts\python.exe -m pip install -r C:\ComfyUI\requirements.txt
curl.exe -L -o C:\ComfyUI\models\checkpoints\sd_xl_base_1.0.safetensors https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors

# 4. GPU 인식 확인 (True 가 나와야 함)
C:\ComfyUI\venv\Scripts\python.exe -c "import torch; print(torch.cuda.is_available())"
```

## 이 레포의 파일

| 파일 | 역할 |
|---|---|
| [`generate.py`](generate.py) | ComfyUI API 호출 스크립트. 서버 자동 기동 → 워크플로 제출 → PNG 저장. `C:\ComfyUI\`에 복사해서 사용 |
| [`skill/SKILL.md`](skill/SKILL.md) | Claude Code 스킬 정의. `~/.claude/skills/draw-local/SKILL.md`로 복사하면 "그려줘" 요청에 자동 발동 |

```powershell
# 배치
Copy-Item generate.py C:\ComfyUI\generate.py
New-Item -ItemType Directory -Force $HOME\.claude\skills\draw-local
Copy-Item skill\SKILL.md $HOME\.claude\skills\draw-local\SKILL.md
```

## 사용법

클로드 코드에서 그냥 **"~그려줘"** 라고 하면 끝. 직접 실행할 수도 있다:

```powershell
C:\ComfyUI\venv\Scripts\python.exe C:\ComfyUI\generate.py "a cute orange cat sitting on a windowsill, warm sunlight, photorealistic"
# → SAVED C:\ComfyUI\output\claude_00001_.png  (seed 640348078, 24s)
```

옵션: `--out 저장경로` `--width/--height` (기본 1024) `--steps` (기본 28) `--cfg` (기본 7.0) `--seed` (재현/변형) `--negative "피할 요소"`

## 결과물 예시 (RTX 4060 Laptop에서 생성)

| 프롬프트 | 결과 |
|---|---|
| `a cute orange cat sitting on a windowsill, warm sunlight, photorealistic` | ![cat](images/orange-cat.jpg) |
| `a serene mountain lake at sunrise, mist over the water, photorealistic` | ![lake](images/mountain-lake.jpg) |
| `Seoul city skyline at sunset, Namsan Tower and Han River, glowing orange and purple sky, cinematic lighting` | ![seoul](images/seoul-sunset.jpg) |

**프롬프트 팁**: ① 영어로 쓸 것 ② `photorealistic`, `cinematic lighting` 같은 스타일 키워드를 뒤에 붙일 것 ③ 피하고 싶은 요소는 네거티브 프롬프트로 분리할 것.

## 실측 성능 (RTX 4060 Laptop 8GB)

- 첫 생성: 약 1분 (서버 기동 + 모델 VRAM 로딩)
- 이후: **장당 20~40초** (1024×1024, 28스텝)
- OOM(메모리 부족) 발생 시: GPU를 쓰는 다른 프로그램(게임 등)을 닫고 재시도

## License

MIT
