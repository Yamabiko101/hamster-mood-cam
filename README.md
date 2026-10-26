# Hamster Mood Cam

Detector local de expresiones faciales que muestra un meme de hámster según la
expresión observada por la cámara. Usa modelos preentrenados de OpenCV y **no
necesita entrenarse con tu rostro**.

## Windows: descargar y abrir

No necesitas instalar Python.

1. Abre [Descargar la última versión](https://github.com/Yamabiko101/hamster-mood-cam/releases/latest).
2. En **Assets**, descarga `HamsterMoodCam-Windows-x64.zip`.
3. Haz clic derecho en el ZIP y selecciona **Extraer todo**.
4. Abre la carpeta extraída y haz doble clic en
   `HamsterMoodCam.exe`.
5. Permite el acceso a la cámara si Windows lo solicita.

Para cerrar, pulsa `q` en la ventana del detector.

### Aviso de Windows SmartScreen

El ejecutable no tiene firma digital. Si SmartScreen muestra una advertencia,
pulsa **Más información** y después **Ejecutar de todas formas**, verificando
antes que el ZIP provenga de este repositorio.

## Borrar de Windows

La aplicación es portable y no crea servicios, entradas de inicio ni claves del
Registro.

1. Cierra el programa.
2. Elimina la carpeta `HamsterMoodCam`.
3. Elimina también el ZIP descargado si todavía lo conservas.

Eso borra todo. Como alternativa, abre `UNINSTALL.bat` dentro de la carpeta y
pulsa `S`.

## Qué aparece al ejecutarlo

- A la izquierda: la cámara, un recuadro facial y la expresión detectada.
- A la derecha: el meme correspondiente.

Solo utiliza la cara más grande que encuentra en el fotograma.

## Privacidad

- Los fotogramas se procesan localmente y solo en memoria.
- No se guardan fotografías, video ni resultados.
- No se entrena ningún modelo con tu rostro.
- La versión portable no necesita Internet.

## Código fuente (opcional)

### Windows

Requiere Python 3.12 instalado desde
[python.org](https://www.python.org/downloads/windows/), con **Add Python to
PATH** activado.

Si prefieres usar el código en vez del ZIP terminado, descárgalo, extráelo y haz
doble clic en:

```text
run_windows.bat
```

La primera ejecución prepara todo dentro de esa misma carpeta. Las siguientes
ejecuciones funcionan sin Internet.

### macOS

```bash
./run.command
```

Si macOS bloquea el archivo, haz clic derecho sobre `run.command`, elige
**Abrir** y confirma.

## Desarrollo y pruebas

```bash
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install pytest
python -m pytest -q
```

La integración continua ejecuta las pruebas en Windows y Linux. Las versiones
etiquetadas con `v*` generan automáticamente el ZIP portable de Windows mediante
GitHub Actions.

## Tecnología

- OpenCV YuNet para detección facial y cinco puntos faciales.
- OpenCV Zoo Progressive Teacher / MobileFaceNet para expresiones.
- NumPy para el procesamiento en memoria.
- PyInstaller para el paquete portable de Windows.

El modelo de expresiones produce siete categorías. Para conservar los cinco
memes del proyecto, `disgust` se agrupa con `angry` y `fearful` con `surprise`.

## Limitaciones

- La clasificación representa una estimación visual de la expresión, no el
  estado emocional real de una persona.
- El paquete publicado está dirigido a Windows x64.
- El ejecutable no está firmado digitalmente.
- La cámara debe estar disponible y no puede estar ocupada por otra aplicación.

## Licencias y créditos

Este proyecto deriva de
[mtysac/meme-facerecognition](https://github.com/mtysac/meme-facerecognition)
y conserva su licencia MIT. Los modelos preentrenados y sus huellas SHA-256 se
documentan en [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
