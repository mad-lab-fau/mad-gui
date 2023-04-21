import argparse
import sys
from pathlib import Path

import pyqtgraph
from PySide2.QtWidgets import QApplication

from mad_gui.config import BaseSettings, BaseTheme
from mad_gui.plot_tools.labels import BaseEventLabel, BaseRegionLabel
from mad_gui.plugins.base import BasePlugin
from mad_gui.plugins.example import (
    EnergyCalculator,
    ExampleExporter,
    ExampleImporter,
    StationaryMomentsDetector,
    ActivityLabel,
    Stride,
    MyEvent,
)
from mad_gui.windows import MainWindow
from typing import Optional, Sequence, Type


def start_gui(
    data_dir=Path("."),
    plugins: Optional[Sequence[BasePlugin]] = (
        ExampleImporter,
        StationaryMomentsDetector,
        EnergyCalculator,
        ExampleExporter,
    ),
    labels: Optional[Sequence[BaseRegionLabel]] = (ActivityLabel, Stride),
    events: Optional[Sequence[BaseEventLabel]] = (MyEvent,),
    settings: Optional[Type[BaseSettings]] = BaseSettings,
    theme: Optional[Type[BaseTheme]] = BaseTheme,
    use_opengl: bool = True,
):
    """Use this function to start the GUI and pass your plugins, like importers and algorithms to it.

    Please look at the `See Also` section below, to learn more about how to create objects of the classes you can
    pass to this function.

    Parameters
    ----------
    events
        The event labels you want to use. They inherit from :class:`~mad_gui.plot_tools.labels.BaseEventLabel`.
    data_dir
        The base path where there user will be directed to when opening a file.
    plugins
        Mostly you will adapt the GUI via this. The plugins must inherit from either of these:
        :class:`~mad_gui.plugins.BaseImporter`, :class:`~mad_gui.plugins.BaseExporter`,
        :class:`~mad_gui.plugins.BaseAlgorithm`.
    labels
        The region labels you want to use. They inherit from :class:`~mad_gui.plot_tools.labels.BaseRegionLabel`.
    settings
        Change some settings like the snap range, if you set your label's `snap_to_min` or `snap_to_max` to `True`
    theme
        Change the two main colors (light and dark) of the GUI using this
    use_opengl
        If you want to use OpenGL for the plots, set this to `True`.
        On some operating systems, this makes zooming and scrolling much smoother.
        However, under Linux this can cause degraded performance, so you can set it to `False` there.


    """
    # Create the Qt Application
    pyqtgraph.setConfigOptions(useOpenGL=use_opengl, useNumba=True)
    app = QApplication(sys.argv)
    form = MainWindow(
        parent=app, data_dir=data_dir, settings=settings, theme=theme, plugins=plugins, labels=labels, events=events
    )
    form.show()

    sys.exit(app.exec_())


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir")
    args = parser.parse_args()
    start_gui(args.data_dir)
