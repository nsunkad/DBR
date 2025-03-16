import os
import sys
import subprocess


def gen_venv(venv_dir="virtualenv"):
    """Creates a Python virtual environment in specified directory."""

    print(f"Creating virtual environment in '{venv_dir}'...")
    subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)

    # Install dependencies
    pip_path = os.path.join(venv_dir, "bin", "pip")
    packages = ["black", "mypy"]
    subprocess.run([pip_path, "install"] + packages, check=True)
    print("Done")


gen_venv()