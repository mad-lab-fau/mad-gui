# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os
HERE = os.path.abspath(".")

import sys
venv_path = sys.executable.split(os.sep)[-3]

if not os.path.exists(venv_path):
    raise FileNotFoundError(f"Apparently there is no virtual environment in {venv_path} although I was expecting that. "\
                            "Please see https://github.com/mad-lab-fau/mad-gui/blob/main/docs/developer_guidelines.rst#6-creating-an-executable "\
                            "for information why I'm expecting that."\
                            "\n In case your venv is in a different location, please change it in `pyinstaller.spec`")

import platform
from pathlib import Path
import warnings
if platform.system() == "Windows":
    site_packages_path = f"{venv_path}/Lib/site-packages"
elif platform.system() in ["Linux", "Darwin"]:
    python_dirs = os.listdir(Path(venv_path) / "lib/")
    warnings.warn(
        f"dodo.py: Assuming your python 3.7 installation is in {Path(venv_path)}/lib/{python_dirs[0]}"
    )
    site_packages_path = f"{venv_path}/lib/{python_dirs[0]}/site-packages"
else:
    raise ValueError("What OS is this?!")

a = Analysis(['mad_gui/start_gui.py'],
             pathex=[HERE, site_packages_path],
             binaries=[],
             datas=[(f'{site_packages_path}/mad_gui/qt_designer/build/*.py', 'mad_gui/qt_designer/build/'),
                    (f'{HERE}/mad_gui/qt_designer/window_buttons_rc.py', 'mad_gui/qt_designer/'),
                    (f'{HERE}/mad_gui/qt_designer/ui_video.py', 'mad_gui/qt_designer/')],
             hiddenimports=["mouse"],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

if platform.system() != "Darwin":
    splash = Splash('splash.jpg',
                    binaries=a.binaries,
                    datas=a.datas,
                    text_pos=(60, 290),
                    text_size=12,
                    text_color='black',
		    text_default='Starting MaD GUI...')




    exe = EXE(pyz,
              splash,
              splash.binaries,
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,
              [],
              name='mad_gui',
              debug=False,
              bootloader_ignore_signals=False,
              strip=False,
              upx=True,
              upx_exclude=[],
              runtime_tmpdir=None,
              console=True,
              disable_windowed_traceback=False,
              target_arch=None,
              codesign_identity=None,
              entitlements_file=None , icon='mad-runner.ico')

else:
    exe = EXE(pyz,
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,
              [],
              name='mad_gui',
              debug=False,
              bootloader_ignore_signals=False,
              strip=False,
              upx=True,
              upx_exclude=[],
              runtime_tmpdir=None,
              console=True,
              disable_windowed_traceback=False,
              target_arch=None,
              codesign_identity=None,
              entitlements_file=None , icon='mad-runner.ico')
