import argparse
import sys

from PySide2.QtWidgets import QApplication

from mad_gui.config import BaseSettings, BaseTheme
from mad_gui.plugins.base import BasePlugin
from mad_gui.plugins.example import ExampleImporter
from mad_gui.windows import MainWindow
from typing import Sequence, Type


def start_gui(
    data_dir,
    settings: Type[BaseSettings] = BaseSettings,
    theme: Type[BaseTheme] = BaseTheme,
    plugins: Sequence[BasePlugin] = (ExampleImporter,),
):
    # Create the Qt Application
    app = QApplication(sys.argv)
    form = MainWindow(data_dir=data_dir, settings=settings, theme=theme, plugins=plugins)
    form.show()

    sys.exit(app.exec_())


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--base_dir")
    parser.add_argument("--consts_file")
    args = parser.parse_args()
    # TODO: Add Arguments back in
    start_gui(args.base_dir)
