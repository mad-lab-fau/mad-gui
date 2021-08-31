import argparse
import sys
from pathlib import Path

from mad_gui.config import BaseSettings, BaseTheme
from mad_gui.plot_tools.labels import BaseRegionLabel
from mad_gui.plugins.base import BasePlugin
from mad_gui.plugins.example import ExampleAlgorithm, ExampleImporter
from mad_gui.windows import MainWindow
from PySide2.QtWidgets import QApplication

from typing import Sequence, Type


def start_gui(
    base_dir=Path("../example_data/").absolute(),
    settings: Type[BaseSettings] = BaseSettings,
    theme: Type[BaseTheme] = BaseTheme,
    plugins: Sequence[BasePlugin] = (ExampleImporter, ExampleAlgorithm),
    labels: Sequence[BaseRegionLabel] = (BaseRegionLabel,),
):
    # Create the Qt Application
    app = QApplication(sys.argv)
    form = MainWindow(parent=app, data_dir=base_dir, settings=settings, theme=theme, plugins=plugins, labels=labels)
    form.show()

    sys.exit(app.exec_())


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--base_dir")
    args = parser.parse_args()
    start_gui(args.base_dir)
