#!/usr/bin/env bash
# One-time setup per fresh session (~1-2 min). Idempotent.
set -e
pip install --break-system-packages -q skia-python kokoro-onnx scipy soundfile pillow numpy 2>&1 | grep -vi warning || true
mkdir -p /tmp/kokoro
cd /tmp/kokoro
[ -s kokoro-v1.0.onnx ] || curl -sL -o kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -s voices-v1.0.bin ] || curl -sL -o voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
which ffmpeg >/dev/null || { echo "ffmpeg missing"; exit 1; }
python3 -c "import skia, kokoro_onnx, scipy, soundfile, PIL; print('setup ok')"
