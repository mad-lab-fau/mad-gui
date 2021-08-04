# -*- mode: python ; coding: utf-8 -*-

# ('D:/mad-gui_github/mad_gui/qt_designer/*.ui', 'mad_gui/qt_designer/')
block_cipher = None

import os
HERE = os.path.abspath(".")

a = Analysis(['mad_gui/start_gui.py'],
             pathex=[HERE, "D:/mad-gui_github/.venv/Lib/site-packages"],
             binaries=[],
             datas=[('D:/mad-gui_github/.venv/Lib/site-packages/mad_gui/qt_designer/build/*.py', 'mad_gui/qt_designer/build/'),
                    ('D:/mad-gui_github/mad_gui/qt_designer/window_buttons_rc.py', 'mad_gui/qt_designer/'),
                    ('D:/mad-gui_github/mad_gui/qt_designer/ui_video.py', 'mad_gui/qt_designer/')],
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
