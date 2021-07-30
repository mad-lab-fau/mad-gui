from pathlib import Path

from PySide2.QtCore import QCoreApplication
from PySide2.QtWidgets import QFileDialog

from typing import Optional


def ask_for_file_name(base_dir: Path, parent=None) -> Optional[str]:
    data_file = QFileDialog(parent=parent).getOpenFileName(None, "Select file to open", str(base_dir))[0]
    if data_file == "":
        # User clicked cancel
        return None
    return data_file


def set_cursor(window, cursor_type):
    window.setCursor(cursor_type)
    QCoreApplication.processEvents()  # On windows, we have to force GUI to update the cursor
