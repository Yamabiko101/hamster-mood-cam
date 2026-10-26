@echo off
setlocal
set "HAMSTER_APP_DIR=%~dp0"

if not exist "%HAMSTER_APP_DIR%HamsterEmotionDetector.exe" (
  echo No se encontro HamsterEmotionDetector.exe en esta carpeta.
  echo Por seguridad no se eliminara nada.
  pause
  exit /b 1
)

echo Esto eliminara completamente:
echo %HAMSTER_APP_DIR%
echo.
choice /C SN /N /M "Continuar? [S/N]: "
if errorlevel 2 exit /b 0

cd /d "%TEMP%"
start "" /b powershell.exe -NoProfile -WindowStyle Hidden -Command ^
  "Start-Sleep -Seconds 2; Remove-Item -LiteralPath $env:HAMSTER_APP_DIR -Recurse -Force"
exit /b 0
