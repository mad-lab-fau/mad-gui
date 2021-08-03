# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

import os
HERE = os.path.abspath(".")

a = Analysis(['mad_gui/start_gui.py'],
             pathex=[HERE],
             binaries=[],
             datas=[('mad_gui/qt_designer/*.ui', 'mad_gui/qt_designer/'),
                    ('mad_gui/qt_designer/window_buttons_rc.py', 'mad_gui/qt_designer/'),
                    ('mad_gui/qt_designer/ui_video.py', 'mad_gui/qt_designer/')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

splash = Splash('mad_gui/qt_designer/images/logo_mad_man.png',
                binaries=a.binaries,
                datas=a.datas,
                text_pos=(10, 50),
                text_size=12,
                text_color='black')

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          #splash,  
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
