# Cross-Platform Setup Guide

This guide covers the OS-specific steps required to run the Thai ID OCR stack on macOS (Intel/Apple Silicon), Windows, and Ubuntu. Follow the base instructions in the root README first, then apply the relevant platform tweaks below.

## Common Prerequisites
- Python 3.10+
- Node.js 20+
- Git
- [Ollama](https://ollama.com) with the `qwen2.5` model pulled locally
- Adequate disk space (~6 GB) for Ollama + node_modules + venv

## macOS (Apple Silicon / Intel)
1. **Install Homebrew tools**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   brew install git python node ffmpeg libomp
   ```
2. **Python virtual environment**
   ```bash
   cd thai-id-ocr/backend
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Torch wheels**
   - Apple Silicon: the default `pip install torch torchvision torchaudio` will use the Metal backend automatically.
   - Intel macOS: same command installs CPU wheels automatically.
4. **Verify GPU availability (optional)**
   ```python
   import torch
   print("MPS:", torch.backends.mps.is_available())
   print("CUDA:", torch.cuda.is_available())
   ```
5. **Ollama**
   - Download the macOS build, run `ollama pull qwen2.5`, then `ollama run qwen2.5`.
6. **Environment variables**
   ```bash
   export OLLAMA_BASE_URL=http://localhost:11434
   export LOG_TO_CONSOLE=true
   ```

## Windows 11/10 (x64)
1. **Install dependencies**
   - [Python 3.10+ for Windows](https://www.python.org/downloads/windows/)
   - [Node.js 20+](https://nodejs.org/)
   - [Git for Windows](https://git-scm.com/download/win)
   - [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) → install C++ build tools and Windows 10 SDK
2. **Optional GPU (CUDA)**
   - Install [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) + cuDNN if you want GPU acceleration.
   - Install PyTorch with CUDA wheels:
     ```bash
     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
     ```
3. **Virtual environment**
   ```powershell
   cd thai-id-ocr\backend
   py -3.10 -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Install Ollama (Windows)**
   - Use the Windows preview build from Ollama’s website, or run Ollama via WSL (Ubuntu) and point `OLLAMA_BASE_URL` to that instance.
5. **Environment variables** (PowerShell)
   ```powershell
   setx OLLAMA_BASE_URL "http://localhost:11434"
   setx LOG_TO_CONSOLE "true"
   ```
6. **FFmpeg / OpenCV codecs**
   - Install [FFmpeg for Windows](https://www.gyan.dev/ffmpeg/builds/) and add it to PATH for best OCR results.

## Ubuntu 22.04/20.04
1. **System packages**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-venv python3-pip nodejs npm git ffmpeg libsm6 libxext6 libgl1
   ```
2. **Optional CUDA**
   - Install NVIDIA drivers + CUDA toolkit if GPU acceleration is required.
   - Install PyTorch CUDA wheels via `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`.
3. **Virtual environment**
   ```bash
   cd thai-id-ocr/backend
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Ollama on Linux**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull qwen2.5
   ollama run qwen2.5
   ```
5. **Environment variables**
   ```bash
   export OLLAMA_BASE_URL=http://localhost:11434
   export LOG_TO_CONSOLE=true
   ```

## Frontend notes (all platforms)
- Run from `frontend/`: `npm install && npm run dev`
- If encountering `sharp` build issues, reinstall with platform-specific binaries: `npm rebuild sharp`
- For Windows PowerShell, allow script execution: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

## Troubleshooting
| Symptom | Platform Tips | Fix |
| --- | --- | --- |
| `ImportError: libGL.so.1` | Ubuntu | Install `libgl1` (see apt instructions above) |
| `OMP: Error #15` | macOS Intel | Ensure `brew install libomp` and export `DYLD_LIBRARY_PATH=/usr/local/opt/libomp/lib` if needed |
| `MSVCP140.dll missing` | Windows | Install Visual C++ Redistributable / Build Tools |
| `ollama: command not found` | Linux/Win | Confirm Ollama installed or running via WSL, adjust `OLLAMA_BASE_URL` |
| GPU not detected | Any | Check driver/toolkit versions, fallback CPU path remains functional |

With these steps, the backend and frontend should run consistently across macOS (Intel/Apple Silicon), Windows, and Ubuntu.
