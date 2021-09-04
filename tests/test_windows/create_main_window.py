import sys

from mad_gui import BaseSettings, BaseTheme
from mad_gui.plot_tools.labels import BaseRegionLabel
from mad_gui.plugins.example import ExampleImporter
from mad_gui.windows import MainWindow
from PySide2.QtWidgets import QApplication


class Jump(BaseRegionLabel):
    name = "Jump"
    min_height = 0.1
    max_height = 0.5


class Activity(BaseRegionLabel):
    name = "Activity"
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
    labels = (BaseRegionLabel, Activity, Jump)

    form = MainWindow(settings=settings, theme=theme, plugins=plugins, labels=labels)
    return form
