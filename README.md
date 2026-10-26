# Hamster Mood Cam

Hamster Mood Cam usa la cámara de tu computadora y muestra un meme de hámster
según la expresión que detecta. No necesita aprender tu cara y no guarda fotos
ni videos.

## Descargar y usar en Windows

No necesitas saber programar, instalar Python ni abrir una terminal.

### 1. Descargar

Haz clic aquí:

### [⬇️ Descargar Hamster Mood Cam para Windows](https://github.com/Yamabiko101/hamster-mood-cam/releases/latest/download/HamsterMoodCam-Windows-x64.zip)

Tu navegador guardará el archivo `HamsterMoodCam-Windows-x64.zip`, normalmente
en la carpeta **Descargas**.

> No uses el botón verde **Code** de GitHub. Ese botón descarga el código fuente,
> no la aplicación lista para usar.

### 2. Extraer el archivo

1. Abre el **Explorador de archivos**. Es el icono de una carpeta amarilla.
2. En la columna izquierda, abre **Descargas**.
3. Busca `HamsterMoodCam-Windows-x64.zip`.
4. Haz clic derecho sobre el archivo.
5. Selecciona **Extraer todo...**.
6. Pulsa **Extraer**.

Windows abrirá una carpeta nueva. Dentro encontrarás otra carpeta llamada
`HamsterMoodCam`; ábrela.

> No abras el programa directamente dentro del ZIP. Primero debes usar
> **Extraer todo...**.

### 3. Abrir la aplicación

1. Dentro de la carpeta `HamsterMoodCam`, busca `HamsterMoodCam.exe`.
2. Haz doble clic en `HamsterMoodCam.exe`.
3. Si Windows pide permiso para usar la cámara, selecciona **Sí** o **Permitir**.

La primera apertura puede mostrar una advertencia de Windows porque el programa
no tiene una firma digital comercial:

1. Pulsa **Más información**.
2. Pulsa **Ejecutar de todas formas**.

Hazlo solamente si descargaste el archivo desde el enlace de este README.

### 4. Usar y cerrar

- Mira hacia la cámara con buena iluminación.
- La cámara aparece a la izquierda y el meme aparece a la derecha.
- Para cerrar, haz clic dentro de la ventana y pulsa la tecla `Q`.

La aplicación usa solamente la cara más grande que detecta.

## Si la cámara no aparece

1. Cierra Zoom, Meet, Teams u otra aplicación que pueda estar usando la cámara.
2. Abre **Configuración de Windows**.
3. Entra en **Privacidad y seguridad** → **Cámara**.
4. Activa **Acceso a la cámara** y **Permitir que las aplicaciones de escritorio
   accedan a la cámara**.
5. Vuelve a abrir `HamsterMoodCam.exe`.

Comprueba también que ejecutaste el programa desde la carpeta extraída y no
desde dentro del ZIP.

## Borrar completamente

Hamster Mood Cam es portable: no se instala en Windows, no inicia solo y no
añade servicios ni claves al Registro.

1. Cierra Hamster Mood Cam pulsando `Q`.
2. Abre el **Explorador de archivos**.
3. Busca la carpeta `HamsterMoodCam` que extrajiste.
4. Haz clic derecho sobre la carpeta y selecciona **Eliminar**.
5. Elimina también `HamsterMoodCam-Windows-x64.zip` de **Descargas**.

Eso elimina completamente la aplicación. También puedes abrir `UNINSTALL.bat`
dentro de la carpeta y pulsar `S`, pero borrar la carpeta manualmente es
suficiente.

## Privacidad

- La cámara se procesa localmente y solo en memoria.
- No se guardan fotografías, videos ni resultados.
- No se entrena ningún modelo con tu rostro.
- La aplicación descargada funciona sin Internet.

## Limitaciones

- La expresión mostrada es una estimación visual, no el estado emocional real de
  una persona.
- La descarga está preparada para Windows de 64 bits.
- El ejecutable no tiene firma digital comercial, por lo que Windows puede
  mostrar la advertencia explicada anteriormente.

<details>
<summary>Información para desarrolladores</summary>

### Ejecutar el código fuente

En Windows, instala Python 3.12, descarga el código fuente y abre:

```text
run_windows.bat
```

En macOS:

```bash
./run.command
```

La primera ejecución crea un entorno local y descarga aproximadamente 5 MB de
modelos verificados dentro de la carpeta del proyecto.

### Pruebas

```bash
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install pytest
python -m pytest -q
```

El proyecto usa OpenCV YuNet, OpenCV Zoo MobileFaceNet, NumPy y PyInstaller. El
modelo produce siete categorías; `disgust` se agrupa con `angry` y `fearful`
con `surprise` para utilizar los cinco memes disponibles.

</details>

## Licencias y créditos

Este proyecto deriva de
[mtysac/meme-facerecognition](https://github.com/mtysac/meme-facerecognition)
y conserva su licencia MIT. Los modelos y sus huellas SHA-256 se documentan en
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
