import os
import subprocess
import platform
import shutil
import warnings
from pathlib import Path

DOIT_CONFIG = {
    "default_tasks": ["format", "lint", "test", "prepare_build"],
    "backend": "json",
}

HERE = Path(__file__).parent


def task_format():
    """Reformat all files using black."""
    print(HERE)
    return {"actions": [["black", HERE], ["isort", HERE]], "verbosity": 1}


def task_format_check():
    """Check, but not change, formatting using black."""
    print("#################### black ###################")
    print(HERE)
    print(os.listdir(HERE))
    return {"actions": [["black", HERE, "--check"], ["isort", HERE, "--check-only"]], "verbosity": 1}


def task_lint():
    """Lint all files with Prospector."""
    return {"actions": [["prospector", "-X"]], "verbosity": 1}


def task_test():
    """Run Pytest with coverage."""
    return {
        "actions": [["pytest", "--cov=mad_gui", "--cov-config=.coveragerc", "-vv"]],
        "verbosity": 2,
    }


def task_prepare_build():
    """Build a standalone windows executable."""

    import sys

    python_path = sys.executable.split(os.sep)
    venv_path = str(Path(os.sep.join(python_path[:-2])))

    def get_dst_path():
        import platform

        print(f"Going on with {venv_path} as the virtual environment exclusively used for using pyinstaller.")
        arch = platform.system()
        if arch == "Windows":
            return Path(venv_path) / "Lib/site-packages/mad_gui/qt_designer/build/"
        if arch in ["Linux", "Darwin"]:
            python_dirs = os.listdir(Path(venv_path) / "lib/")
            warnings.warn(
                f"dodo.py: Assuming your python installation is in {Path(venv_path)}/lib/{python_dirs[0]}"
            )
            return Path(venv_path) / "lib" / python_dirs[0] / "site-packages/mad_gui/qt_designer/build/"
        raise ValueError("What operating system is this?!")

    def set_up_paths():
        if not os.path.exists(get_dst_path().parent):
            raise FileNotFoundError(
                "Apparently mad_gui is not installed in this environment. Use `pip install mad_gui` to do so."
            )
        dst_path = get_dst_path()
        os.makedirs(dst_path, exist_ok=True)

    def convert_ui_to_py():
        dst_path = get_dst_path()
        ui_files = [file for file in os.listdir(dst_path.parent) if ".ui" in file]
        print("\n")
        for file in ui_files:
            if platform.system() == "Darwin":
                pyside_path = f"{venv_path}/bin/pyside2-uic"
            else:
                pyside_path = "pyside2-uic"
            result = subprocess.check_output("ls /Users/runner/work/mad-gui/mad-gui/.venv/bin")
            print(f"Content of .venv/bin: {result}")
            result = subprocess.check_output(f"{pyside_path} -h")
            print(f"Result: {result}")
            print(f"Converting from: {dst_path.parent}{os.sep}{file}")
            print(f"To: {dst_path}{os.sep}{file.split('.')[0]}.py")
            result = subprocess.check_output(f"{pyside_path} -o {dst_path}{os.sep}{file.split('.')[0]}.py {dst_path.parent}{os.sep}{file}")
            print(f"Conversio result: {result}\n")

        print(
            "Info: These conversions should have taken place in the virtual environment you are going to use with "
            "pyinstaller."
        )

    return {
        "actions": [set_up_paths, convert_ui_to_py],
        "verbosity": 2,
    }


def task_docs():
    """Build the documentation."""
    # Delete Autogenerated files from previous run
    shutil.rmtree(str(HERE / "docs/_build"), ignore_errors=True)
    # Copy the images into the docs folder
    IMAGES_PATH = HERE / "docs/_build/html/images/"
    os.makedirs(IMAGES_PATH)
    for file in list(IMAGES_PATH.glob("*")):
        shutil.copy(str(file), str(IMAGES_PATH / str(file).split(os.sep)[-1]))

    # Copy the image buttons
    for file in list((HERE / "mad_gui/qt_designer/images").glob("*.png")):
        shutil.copy(str(file), str(IMAGES_PATH / str(file).split(os.sep)[-1]))

    if platform.system() == "Windows":
        return {"actions": [[HERE / "docs/make.bat", "html"]], "verbosity": 2}
    return {"actions": [["make", "-C", HERE / "docs", "html"]], "verbosity": 2}
