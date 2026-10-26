from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

import detect_emotion_live as detector


class TestCropToSquare:
    def test_landscape_becomes_square(self):
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        assert detector.crop_to_square(image).shape == (480, 480, 3)

    def test_portrait_becomes_square(self):
        image = np.zeros((640, 480, 3), dtype=np.uint8)
        assert detector.crop_to_square(image).shape == (480, 480, 3)

    def test_center_is_preserved(self):
        image = np.zeros((100, 200, 3), dtype=np.uint8)
        image[:, 50:150] = 255
        assert np.all(detector.crop_to_square(image) == 255)


def test_softmax_returns_probabilities():
    result = detector.softmax(np.array([1.0, 2.0, 3.0]))
    assert result.sum() == pytest.approx(1.0)
    assert np.argmax(result) == 2


def test_extra_emotions_are_mapped_to_existing_overlays():
    source = np.array([0.05, 0.35, 0.20, 0.05, 0.05, 0.05, 0.25])
    emotion, confidence = detector.map_expression_probabilities(source)
    assert emotion == "surprise"
    assert confidence == pytest.approx(0.45)


def test_disgust_is_aggregated_with_angry():
    source = np.array([0.25, 0.30, 0.05, 0.10, 0.10, 0.10, 0.10])
    emotion, confidence = detector.map_expression_probabilities(source)
    assert emotion == "angry"
    assert confidence == pytest.approx(0.55)


def test_invalid_model_output_is_rejected():
    with pytest.raises(ValueError):
        detector.map_expression_probabilities(np.zeros(5))


def test_largest_face_uses_area():
    faces = np.array(
        [
            [0, 0, 30, 30] + [0] * 11,
            [0, 0, 60, 40] + [0] * 11,
        ],
        dtype=np.float32,
    )
    assert detector.largest_face(faces)[2] == 60


def test_align_face_returns_model_input_size():
    frame = np.zeros((160, 160, 3), dtype=np.uint8)
    detection = np.zeros(15, dtype=np.float32)
    detection[4:14] = detector.FER_TEMPLATE.reshape(-1)
    aligned = detector.align_face(frame, detection)
    assert aligned.shape == (112, 112, 3)


def test_existing_model_with_matching_hash_is_not_downloaded(
    tmp_path: Path, monkeypatch
):
    content = b"known model bytes"
    expected_hash = __import__("hashlib").sha256(content).hexdigest()
    monkeypatch.setattr(detector, "MODEL_DIR", tmp_path)
    path = tmp_path / "model.onnx"
    path.write_bytes(content)
    urlopen = MagicMock()
    monkeypatch.setattr(detector.urllib.request, "urlopen", urlopen)

    result = detector.ensure_model(
        {"filename": "model.onnx", "url": "https://invalid", "sha256": expected_hash}
    )

    assert result == path
    urlopen.assert_not_called()


def test_open_camera_uses_default_backend(monkeypatch):
    capture = MagicMock()
    capture.isOpened.return_value = True
    capture.read.return_value = (True, np.zeros((2, 2, 3), dtype=np.uint8))
    video_capture = MagicMock(return_value=capture)
    monkeypatch.setattr(detector.cv2, "VideoCapture", video_capture)
    monkeypatch.setattr(detector, "camera_preflight", MagicMock(return_value=True))

    result = detector.open_camera(0)

    assert result is capture
    video_capture.assert_called_once_with(0)


def test_open_camera_does_not_touch_device_after_failed_preflight(monkeypatch):
    video_capture = MagicMock()
    monkeypatch.setattr(detector.cv2, "VideoCapture", video_capture)
    monkeypatch.setattr(detector, "camera_preflight", MagicMock(return_value=False))

    assert detector.open_camera(0) is None
    video_capture.assert_not_called()


def test_camera_check_command_for_source(monkeypatch):
    monkeypatch.delattr(detector.sys, "frozen", raising=False)
    command = detector.camera_check_command(2)
    assert command[0] == detector.sys.executable
    assert command[-2:] == ["--camera-check", "2"]
    assert command[1].endswith("detect_emotion_live.py")


def test_camera_check_command_for_packaged_executable(monkeypatch):
    monkeypatch.setattr(detector.sys, "frozen", True, raising=False)
    assert detector.camera_check_command(1) == [
        detector.sys.executable,
        "--camera-check",
        "1",
    ]


def test_windows_camera_help(monkeypatch):
    monkeypatch.setattr(detector.sys, "platform", "win32")
    assert "Windows Settings" in detector.camera_help()
