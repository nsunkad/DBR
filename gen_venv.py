import os
import sys
import subprocess


def gen_venv(venv_dir="virtualenv"):
    """Creates a Python virtual environment in specified directory."""

    print(f"Creating virtual environment in '{venv_dir}'...")
    subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)

    # Install dependencies
    pip_path = os.path.join(venv_dir, "bin", "pip")
    subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])
    print("Done")


gen_venv()