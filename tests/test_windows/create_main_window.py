import sys

from mad_gui import BaseSettings, BaseTheme
from mad_gui.plot_tools.labels import BaseRegionLabel
from mad_gui.plugins.example import ExampleImporter
from mad_gui.windows import MainWindow
from PySide2.QtWidgets import QApplication


class MyLabel(BaseRegionLabel):
    name = "Mei label"
    min_height = 0.1
    max_height = 0.5


class MyOtherLabel(BaseRegionLabel):
    name = "Mei anners label"
    min_height = 0.8
    max_height = 1


def get_main_window():
    if not QApplication.instance():
        # Create the Qt Application
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    settings = BaseSettings
    theme = BaseTheme
    plugins = (ExampleImporter,)
    labels = (BaseRegionLabel,)

    form = MainWindow(settings=settings, theme=theme, plugins=plugins, labels=labels)
    return form
