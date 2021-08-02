import argparse
import sys

from PySide2.QtWidgets import QApplication

from mad_gui.config import BaseSettings, BaseTheme
from mad_gui.plot_tools import BaseRegionLabel
from mad_gui.plugins.base import BasePlugin
from mad_gui.plugins.example import ExampleImporter
from mad_gui.windows import MainWindow
from typing import Sequence, Type


class MyLabel(BaseRegionLabel):
    name = "Mei label"
    min_height = 0.1
    max_height = 0.5


class MyOtherLabel(BaseRegionLabel):
    name = "Mei anners label"
    min_height = 0.8
    max_height = 1


def start_gui(
    data_dir,
    settings: Type[BaseSettings] = BaseSettings,
    theme: Type[BaseTheme] = BaseTheme,
    plugins: Sequence[BasePlugin] = (ExampleImporter,),
    labels: Sequence[BaseRegionLabel] = (MyLabel, MyOtherLabel),
):
    # Create the Qt Application
    app = QApplication(sys.argv)
    form = MainWindow(data_dir=data_dir, settings=settings, theme=theme, plugins=plugins, labels=labels)
    form.show()

    sys.exit(app.exec_())


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--base_dir")
    args = parser.parse_args()
    start_gui(args.base_dir)
