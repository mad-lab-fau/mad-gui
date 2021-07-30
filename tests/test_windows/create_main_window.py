import sys

from PySide2.QtWidgets import QApplication

from mad_gui import BaseSettings, BaseTheme
from mad_gui.plugins.example import ExampleImporter
from mad_gui.start_gui import MyLabel, MyOtherLabel
from mad_gui.windows import MainWindow


def get_main_window():
    if not QApplication.instance():
        # Create the Qt Application
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    settings = BaseSettings
    theme = BaseTheme
    plugins = (ExampleImporter,)
    labels = (MyLabel, MyOtherLabel)

    form = MainWindow(settings=settings, theme=theme, plugins=plugins, labels=labels)
    return form
