#!/bin/bash
set -e

# Limpa locks residuais do X11 e Chromium
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99 || true
rm -f /app/session/profile/Singleton* || true

echo "[*] Iniciando servidor Xvfb na porta de display :99..."
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!

export DISPLAY=:99
sleep 1

echo "[*] Display :99 ativo. Iniciando Uvicorn LinkedIn Bridge..."
exec uvicorn app:app --host 0.0.0.0 --port 8000
