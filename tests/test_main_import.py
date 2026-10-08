import subprocess
import sys


def test_main_can_be_imported_without_running_menu():
    proc = subprocess.run(
        [sys.executable, "-c", "import main; print('IMPORT_OK')"],
        cwd=".",
        capture_output=True,
        text=True,
        timeout=5,
    )

    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert "IMPORT_OK" in proc.stdout
