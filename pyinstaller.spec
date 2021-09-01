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

site_packages_path = f"{venv_path}/Lib/site-packages"

a = Analysis(['mad_gui/start_gui.py'],
             pathex=[HERE, site_packages_path],
             binaries=[],
             datas=[(f'{venv_path}/Lib/site-packages/mad_gui/qt_designer/build/*.py', 'mad_gui/qt_designer/build/'),
                    (f'{HERE}/mad_gui/qt_designer/window_buttons_rc.py', 'mad_gui/qt_designer/'),
                    (f'{HERE}/mad_gui/qt_designer/ui_video.py', 'mad_gui/qt_designer/')],
             hiddenimports=[],
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

# in case of using --onefile remove splash.binaries from exe above and activate this below
#coll = COLLECT(exe,
#               splash.binaries,     # <-- splash binaries
#               )
