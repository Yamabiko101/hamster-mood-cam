#!/bin/zsh

set -u

PROJECT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
cd "$PROJECT_DIR" || exit 1

pause_on_error() {
  local exit_code="$1"
  if (( exit_code != 0 )); then
    echo
    echo "No se pudo iniciar el detector. Revisa el mensaje anterior."
    echo "Presiona cualquier tecla para cerrar."
    read -k 1
  fi
  exit "$exit_code"
}

if ! command -v python3 >/dev/null 2>&1; then
  echo "Falta Python 3. Instálalo desde https://www.python.org/downloads/macos/"
  pause_on_error 1
fi

if [[ ! -x "venv/bin/python" ]]; then
  echo "Preparando el entorno local..."
  python3 -m venv venv || pause_on_error $?
fi

if ! venv/bin/python -c "import cv2, numpy" >/dev/null 2>&1; then
  echo "Instalando dependencias dentro de la carpeta del proyecto..."
  venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt \
    || pause_on_error $?
fi

venv/bin/python -u detect_emotion_live.py
pause_on_error $?
