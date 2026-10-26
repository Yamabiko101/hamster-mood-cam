@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_EXE=venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
  where py >nul 2>nul
  if errorlevel 1 (
    where python >nul 2>nul
    if errorlevel 1 goto no_python
    echo Preparando el entorno local...
    python -m venv venv
    if errorlevel 1 goto setup_error
  ) else (
    echo Preparando el entorno local...
    py -3.12 -m venv venv >nul 2>nul
    if errorlevel 1 py -3 -m venv venv
    if errorlevel 1 goto setup_error
  )
)

"%PYTHON_EXE%" -c "import cv2, numpy" >nul 2>nul
if errorlevel 1 (
  echo Instalando dependencias dentro de esta carpeta...
  "%PYTHON_EXE%" -m pip install --disable-pip-version-check -r requirements.txt
  if errorlevel 1 goto setup_error
)

"%PYTHON_EXE%" -u detect_emotion_live.py
if errorlevel 1 goto app_error
exit /b 0

:no_python
echo No se encontro Python 3.12.
echo Instala Python desde https://www.python.org/downloads/windows/
echo Durante la instalacion activa "Add Python to PATH".
pause
exit /b 1

:setup_error
echo.
echo No se pudo preparar el entorno local.
pause
exit /b 1

:app_error
echo.
echo El detector termino con un error. Revisa el mensaje anterior.
pause
exit /b 1
