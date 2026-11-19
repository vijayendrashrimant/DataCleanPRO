#!/usr/bin/env python3
"""
DataCleanPro — Build API executable
Builds a self-contained binary so users don't need Python installed.

Usage:
    python build_exe.py           # uses venv if present, else system Python
    python build_exe.py --clean   # delete dist/ and build/ first

Output:
    backend/dist/datacleanpro_api        (Linux / macOS)
    backend/dist/datacleanpro_api.exe    (Windows)
"""

import subprocess
import sys
import os
import shutil
import argparse

ROOT = os.path.dirname(os.path.abspath(__file__))


def find_python_and_pip():
    """Return (python_exe, pip_exe) from venv if present, else system."""
    venv = os.path.join(ROOT, "venv")
    if sys.platform == "win32":
        py  = os.path.join(venv, "Scripts", "python.exe")
        pip = os.path.join(venv, "Scripts", "pip.exe")
    else:
        py  = os.path.join(venv, "bin", "python")
        pip = os.path.join(venv, "bin", "pip")

    if os.path.isfile(py):
        return py, pip

    # Fall back to system Python
    return sys.executable, shutil.which("pip") or "pip"


def run(cmd, **kwargs):
    print(f"\n  $ {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        print(f"\n  ✗ Command failed (exit {result.returncode})")
        sys.exit(result.returncode)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true", help="Remove dist/ and build/ before building")
    args = parser.parse_args()

    print("╔══════════════════════════════════════════════╗")
    print("║   DataCleanPro — Build API Executable        ║")
    print("╚══════════════════════════════════════════════╝")

    python, pip = find_python_and_pip()
    print(f"\n  Python : {python}")
    print(f"  Pip    : {pip}")

    # ── 1. Clean previous build ─────────────────────────────────────────────
    if args.clean:
        for d in ("dist", "build"):
            path = os.path.join(ROOT, d)
            if os.path.isdir(path):
                print(f"\n▶ Removing {path} ...")
                shutil.rmtree(path)

    # ── 2. Ensure PyInstaller is installed ──────────────────────────────────
    print("\n▶ Checking PyInstaller...")
    try:
        result = subprocess.run(
            [python, "-c", "import PyInstaller; print(PyInstaller.__version__)"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            print(f"  ✓ PyInstaller {result.stdout.strip()} already installed")
        else:
            raise ImportError
    except (ImportError, FileNotFoundError):
        print("  Installing PyInstaller...")
        run([pip, "install", "pyinstaller", "--quiet"])

    # ── 3. Ensure all requirements are installed ────────────────────────────
    print("\n▶ Installing / verifying requirements...")
    run([pip, "install", "-r", os.path.join(ROOT, "requirements.txt"), "--quiet"])

    # ── 4. Run PyInstaller ──────────────────────────────────────────────────
    print("\n▶ Building executable (this may take 1–3 minutes)...")
    spec = os.path.join(ROOT, "datacleanpro_api.spec")
    run(
        [python, "-m", "PyInstaller", spec, "--noconfirm", "--distpath",
         os.path.join(ROOT, "dist"), "--workpath", os.path.join(ROOT, "build")],
        cwd=ROOT,
    )

    # ── 5. Verify output ────────────────────────────────────────────────────
    exe_name = "datacleanpro_api.exe" if sys.platform == "win32" else "datacleanpro_api"
    exe_path = os.path.join(ROOT, "dist", exe_name)

    if os.path.isfile(exe_path):
        size_mb = os.path.getsize(exe_path) / 1_048_576
        print(f"\n✅ Executable ready: {exe_path}  ({size_mb:.1f} MB)")
        print(f"\n   Copy it to frontend/api/ or run ./run.sh — it will be found automatically.")
    else:
        print(f"\n✗ Expected output not found: {exe_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
