from typing import TYPE_CHECKING

import pyqtgraph as pg
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import QApplication

if TYPE_CHECKING:
    from mad_gui.plot_tools.plots import SensorPlot


class BaseModeHandler:
    mode: str

    def __init__(self, plot: "SensorPlot"):
        self.plot = plot
        # This makes sure that the correct plot has focus when entering a new mode and can accept keyboard inputs
        # TODO: Should this be handled here on an application level?
        pos = QCursor.pos()
        active_widget = QApplication.widgetAt(pos)
        if active_widget:
            active_widget.setFocus()
        self._active = True

    def handle_key_press(self, ev):
        """What exactly should be done if a key is pressed needs to be defined by children."""

    def handle_mouse_click(self, ev):
        pg.PlotWidget.mousePressEvent(self.plot, ev)

    def handle_mouse_movement(self, ev):
        pg.PlotWidget.mouseMoveEvent(self.plot, ev)

    def deactivate(self):
        self._active = False
