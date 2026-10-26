from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_windows_launcher_keeps_environment_inside_project():
    launcher = (ROOT / "run_windows.bat").read_text(encoding="utf-8")
    assert 'cd /d "%~dp0"' in launcher
    assert 'venv\\Scripts\\python.exe' in launcher
    assert "rmdir" not in launcher.lower()
    assert "remove-item" not in launcher.lower()


def test_uninstaller_only_targets_its_own_folder():
    uninstaller = (
        ROOT / "packaging" / "windows" / "UNINSTALL.bat"
    ).read_text(encoding="utf-8")
    assert 'set "HAMSTER_MOOD_CAM_DIR=%~dp0"' in uninstaller
    assert 'if not exist "%HAMSTER_MOOD_CAM_DIR%HamsterMoodCam.exe"' in uninstaller
    assert "Remove-Item -LiteralPath $env:HAMSTER_MOOD_CAM_DIR" in uninstaller


def test_release_zip_contains_top_level_application_folder():
    workflow = (
        ROOT / ".github" / "workflows" / "release-windows.yml"
    ).read_text(encoding="utf-8")
    assert "-Path dist/HamsterMoodCam `" in workflow
    assert "-Path dist/HamsterMoodCam/* `" not in workflow
