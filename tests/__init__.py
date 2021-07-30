import sys
from pathlib import Path

# make sure window_buttons_rc is found
sys.path.append(str((Path(__file__).parent.parent / "mad_gui" / "qt_designer").absolute()))
