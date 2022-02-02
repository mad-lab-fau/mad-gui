import sys

from PySide2.QtWidgets import QApplication

from mad_gui import BaseSettings, BaseTheme
from mad_gui.plot_tools.labels import BaseEventLabel, BaseRegionLabel
from mad_gui.plugins.example import ExampleImporter
from mad_gui.windows import MainWindow


class Peak(BaseEventLabel):
    name = "Peak"
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

    print(str(app))

    settings = BaseSettings
    theme = BaseTheme

    form = MainWindow(
        settings=settings, theme=theme, plugins=[ExampleImporter], labels=[BaseRegionLabel, Activity], events=[Peak]
    )
    return form
