from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Optional

import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
OVERLAY_DIR = BASE_DIR / "overlays"
DISPLAY_SIZE = 480
WINDOW_NAME = "Hamster Mood Cam"

EMOTIONS = ("angry", "happy", "neutral", "sad", "surprise")
SOURCE_EMOTIONS = (
    "angry",
    "disgust",
    "fearful",
    "happy",
    "neutral",
    "sad",
    "surprised",
)
EMOTION_MAP = {
    "angry": "angry",
    "disgust": "angry",
    "fearful": "surprise",
    "happy": "happy",
    "neutral": "neutral",
    "sad": "sad",
    "surprised": "surprise",
}

FER_MODEL = {
    "filename": "facial_expression_recognition_mobilefacenet_2022july.onnx",
    "url": (
        "https://huggingface.co/opencv/facial_expression_recognition/resolve/main/"
        "facial_expression_recognition_mobilefacenet_2022july.onnx"
    ),
    "sha256": "4f61307602fc089ce20488a31d4e4614e3c9753a7d6c41578c854858b183e1a9",
}
YUNET_MODEL = {
    "filename": "face_detection_yunet_2023mar.onnx",
    "url": (
        "https://huggingface.co/opencv/face_detection_yunet/resolve/main/"
        "face_detection_yunet_2023mar.onnx"
    ),
    "sha256": "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4",
}

FER_TEMPLATE = np.array(
    [
        [38.2946, 51.6963],
        [73.5318, 51.5014],
        [56.0252, 71.7366],
        [41.5493, 92.3655],
        [70.7299, 92.2041],
    ],
    dtype=np.float32,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_model(spec: dict[str, str]) -> Path:
    MODEL_DIR.mkdir(exist_ok=True)
    destination = MODEL_DIR / spec["filename"]

    if destination.exists() and sha256_file(destination) == spec["sha256"]:
        return destination

    if destination.exists():
        destination.unlink()

    temporary = destination.with_suffix(destination.suffix + ".download")
    temporary.unlink(missing_ok=True)
    print(f"Downloading {spec['filename']} ...")

    try:
        with urllib.request.urlopen(spec["url"], timeout=60) as response:
            with temporary.open("wb") as file:
                shutil.copyfileobj(response, file)

        actual_hash = sha256_file(temporary)
        if actual_hash != spec["sha256"]:
            raise RuntimeError(
                f"Invalid SHA-256 for {spec['filename']}: {actual_hash}"
            )
        temporary.replace(destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    print(f"Saved {destination.relative_to(BASE_DIR)}")
    return destination


def ensure_models() -> tuple[Path, Path]:
    return ensure_model(YUNET_MODEL), ensure_model(FER_MODEL)


def load_overlays() -> dict[str, np.ndarray]:
    overlays: dict[str, np.ndarray] = {}
    for emotion in EMOTIONS:
        path = OVERLAY_DIR / f"{emotion}.png"
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(f"Missing overlay: {path}")
        overlays[emotion] = cv2.resize(image, (DISPLAY_SIZE, DISPLAY_SIZE))
    return overlays


def softmax(values: np.ndarray) -> np.ndarray:
    flattened = np.asarray(values, dtype=np.float32).reshape(-1)
    shifted = flattened - np.max(flattened)
    exponentials = np.exp(shifted)
    return exponentials / np.sum(exponentials)


def map_expression_probabilities(
    source_probabilities: np.ndarray,
) -> tuple[str, float]:
    probabilities = np.asarray(source_probabilities, dtype=np.float32).reshape(-1)
    if probabilities.size != len(SOURCE_EMOTIONS):
        raise ValueError(
            f"Expected {len(SOURCE_EMOTIONS)} emotion scores, got {probabilities.size}"
        )

    mapped = {emotion: 0.0 for emotion in EMOTIONS}
    for source, probability in zip(SOURCE_EMOTIONS, probabilities):
        mapped[EMOTION_MAP[source]] += float(probability)

    emotion = max(mapped, key=mapped.get)
    return emotion, mapped[emotion]


def align_face(frame: np.ndarray, detection: np.ndarray) -> np.ndarray:
    landmarks = np.asarray(detection[4:14], dtype=np.float32).reshape(5, 2)
    transform, _ = cv2.estimateAffinePartial2D(
        landmarks,
        FER_TEMPLATE,
        method=cv2.LMEDS,
    )
    if transform is None:
        raise RuntimeError("Could not align detected face")
    return cv2.warpAffine(frame, transform, (112, 112))


class EmotionRecognizer:
    def __init__(self, model_path: Path) -> None:
        self.net = cv2.dnn.readNet(str(model_path))
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    def predict(self, frame: np.ndarray, detection: np.ndarray) -> tuple[str, float]:
        aligned = align_face(frame, detection)
        rgb = cv2.cvtColor(aligned, cv2.COLOR_BGR2RGB)
        normalized = (rgb.astype(np.float32) / 255.0 - 0.5) / 0.5
        blob = cv2.dnn.blobFromImage(normalized)
        self.net.setInput(blob, "data")
        logits = self.net.forward("label")
        return map_expression_probabilities(softmax(logits))


def create_face_detector(model_path: Path):
    return cv2.FaceDetectorYN.create(
        model=str(model_path),
        config="",
        input_size=(320, 320),
        score_threshold=0.7,
        nms_threshold=0.3,
        top_k=5000,
        backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
        target_id=cv2.dnn.DNN_TARGET_CPU,
    )


def camera_check(index: int = 0) -> int:
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        cap.release()
        return 1
    try:
        for _ in range(10):
            ok, frame = cap.read()
            if ok and frame is not None and frame.size:
                return 0
            time.sleep(0.05)
        return 1
    finally:
        cap.release()


def camera_check_command(index: int) -> list[str]:
    if getattr(sys, "frozen", False):
        return [sys.executable, "--camera-check", str(index)]
    return [
        sys.executable,
        str(Path(__file__).resolve()),
        "--camera-check",
        str(index),
    ]


def camera_help() -> str:
    if sys.platform == "win32":
        return (
            "Close other camera apps and allow camera access in Windows "
            "Settings > Privacy & security > Camera."
        )
    if sys.platform == "darwin":
        return (
            "Close other camera apps and allow camera access in System Settings "
            "> Privacy & Security > Camera."
        )
    return "Close other camera apps and check the camera permission."


def camera_preflight(index: int = 0, timeout: float = 8.0) -> bool:
    try:
        result = subprocess.run(
            camera_check_command(index),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
            check=False,
            creationflags=(
                getattr(subprocess, "CREATE_NO_WINDOW", 0)
                if sys.platform == "win32"
                else 0
            ),
        )
    except subprocess.TimeoutExpired:
        return False
    return result.returncode == 0


def open_camera(index: int = 0) -> Optional[cv2.VideoCapture]:
    print("Opening camera ...")
    if not camera_preflight(index):
        print(f"The camera is not returning images. {camera_help()}")
        return None

    time.sleep(0.2)
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        cap.release()
        print(f"Could not open the camera. {camera_help()}")
        return None
    print("Camera ready")
    return cap


def crop_to_square(image: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    size = min(height, width)
    top = (height - size) // 2
    left = (width - size) // 2
    return image[top : top + size, left : left + size]


def largest_face(faces: Optional[np.ndarray]) -> Optional[np.ndarray]:
    if faces is None or len(faces) == 0:
        return None
    return max(faces, key=lambda face: float(face[2] * face[3]))


def run() -> int:
    try:
        yunet_path, fer_path = ensure_models()
        overlays = load_overlays()
        detector = create_face_detector(yunet_path)
        recognizer = EmotionRecognizer(fer_path)
    except Exception as error:
        print(f"Startup error: {error}")
        return 1

    camera = open_camera()
    if camera is None:
        return 1

    blank_panel = np.full(
        (DISPLAY_SIZE, DISPLAY_SIZE, 3), 255, dtype=np.uint8
    )
    print("Hamster Mood Cam started. Press q to quit.")

    try:
        while True:
            ok, frame = camera.read()
            if not ok or frame is None or not frame.size:
                print("Camera stopped providing frames. Exiting.")
                return 1
            frame = cv2.flip(frame, 1)
            height, width = frame.shape[:2]
            detector.setInputSize((width, height))
            _, detected_faces = detector.detect(frame)
            face = largest_face(detected_faces)
            current_overlay = blank_panel

            if face is not None:
                emotion, confidence = recognizer.predict(frame, face)
                x, y, face_width, face_height = face[:4].astype(int)
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + face_width, y + face_height),
                    (0, 255, 0),
                    2,
                )
                cv2.putText(
                    frame,
                    f"{emotion} ({confidence:.2f})",
                    (max(x, 0), max(y - 10, 25)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )
                current_overlay = overlays[emotion]

            camera_panel = cv2.resize(
                crop_to_square(frame),
                (DISPLAY_SIZE, DISPLAY_SIZE),
            )
            cv2.imshow(WINDOW_NAME, np.hstack([camera_panel, current_overlay]))

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        camera.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--camera-check":
        raise SystemExit(camera_check(int(sys.argv[2])))
    raise SystemExit(run())
