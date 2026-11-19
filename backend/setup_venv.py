"""Run once to create the Python venv: python setup_venv.py"""
import subprocess, sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
VENV = os.path.join(ROOT, "venv")

def run(cmd):
    print(f"  $ {' '.join(cmd)}")
    r = subprocess.run(cmd)
    if r.returncode != 0: sys.exit(r.returncode)

print("DataCleanPro — Backend Setup")
if not os.path.isdir(VENV):
    run([sys.executable, "-m", "venv", VENV])

pip = os.path.join(VENV, "Scripts" if sys.platform == "win32" else "bin", "pip")
run([pip, "install", "--upgrade", "pip", "-q"])
run([pip, "install", "-r", os.path.join(ROOT, "requirements.txt"), "-q"])
print("\n✅ Done! Run ./run.sh (or run.bat) from the project root to start.")
