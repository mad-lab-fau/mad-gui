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


class Activity(BaseRegionLabel):
   # This label will always be shown at the upper 20% of the plot view
   min_height = 0.8
   max_height = 1
   name = "Activity"
   descriptions = {"stand": None, "walk": ["fast", "slow"], "jump": None}


class Jump(BaseRegionLabel):
   # This label will always be shown at the upper 20% of the plot view
   min_height = 0
   max_height = 0.7
   name = "Jump"
   descriptions = {"high": None, "not so high": None}



def start_gui(
    data_dir=Path("../example_data/").absolute(),
    settings: Type[BaseSettings] = BaseSettings,
    theme: Type[BaseTheme] = BaseTheme,
    plugins: Sequence[BasePlugin] = (ExampleImporter, ExampleAlgorithm),
    labels: Sequence[BaseRegionLabel] = (Activity, Jump),
):
    # Create the Qt Application
    app = QApplication(sys.argv)
    form = MainWindow(parent=app, data_dir=data_dir, settings=settings, theme=theme, plugins=plugins, labels=labels)
    form.show()

    sys.exit(app.exec_())


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir")
    args = parser.parse_args()
    start_gui(args.data_dir)
