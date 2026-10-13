"""Install the produced wheel into a clean venv and run installed entry points."""

import os
import subprocess
import tempfile
import venv
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
wheels = list((root / "dist").glob("*.whl"))
if len(wheels) != 1:
    raise SystemExit("Build exactly one wheel first: python -m build")
wheel = wheels[0]
with zipfile.ZipFile(wheel) as archive:
    for name in archive.namelist():
        if name.startswith(("tests/", "docs/")) or Path(name).name.startswith(".env"):
            raise SystemExit("Development files or credentials found in wheel")
with tempfile.TemporaryDirectory(prefix="pan123-wheel-") as temp:
    environment = Path(temp) / "venv"
    venv.create(environment, with_pip=True)
    bin_dir = environment / ("Scripts" if os.name == "nt" else "bin")
    python = bin_dir / ("python.exe" if os.name == "nt" else "python")
    command = bin_dir / ("pan123.exe" if os.name == "nt" else "pan123")
    subprocess.run([str(python), "-m", "pip", "install", str(wheel)], check=True)
    subprocess.run([str(command), "--version"], cwd=temp, check=True)
    subprocess.run([str(command), "file", "upload", "--help"], cwd=temp, check=True)
    subprocess.run([str(python), "-m", "pan123_cli", "--help"], cwd=temp, check=True)
print("Clean wheel installation and entry points verified.")
