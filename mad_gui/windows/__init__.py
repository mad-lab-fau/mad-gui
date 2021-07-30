# pylint: skip-file
"""The :py:mod:`mad_gui.windows` keeps files for creating a set of windows.
"""

from pathlib import Path

import sys

# make sure window_buttons_rc is found
sys.path.append(str((Path(__file__).parent.parent.parent / "mad_gui" / "qt_designer").absolute()))


# from mad_gui.windows.plugin_selection import LoadDataWindow, ExportResultsWindow, BasePluginSelector
from mad_gui.windows.video_window import VideoWindow
from mad_gui.components.dialogs.user_information import UserInformation
from mad_gui.windows.main import MainWindow

__all__ = [
    "MainWindow",
    "VideoWindow",
    "UserInformation",
]
