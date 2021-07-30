"""This module keeps a class to create plots with IMU data and annotations. The annotations are kept in a separate
class."""

import numpy as np
import pandas as pd

from mad_gui.models.global_data import PlotData
from mad_gui.models.ui_state import MODES
from mad_gui.plot_tools.base_label import BaseRegionLabel
from mad_gui.plot_tools.base_plot import BasePlot
from mad_gui.plot_tools.sensor_plot import SensorPlotState
from mad_gui.plot_tools.sensor_plot_mode_handler import BaseModeHandler, InvestigateModeHandler
from mad_gui.plot_tools.video_plot_mode_handler import SyncModeHandler
from mad_gui.state_keeper import StateKeeper
from typing import Dict, List, Optional, Type


class VideoPlot(BasePlot):
    """A graph of this class will be shown in the main window in order to synchronize video data with sensor data."""

    MODE_HANDLER: Dict[MODES, Type[BaseModeHandler]] = {
        "investigate": InvestigateModeHandler,
        "edit": InvestigateModeHandler,
        "remove": InvestigateModeHandler,
        "add": InvestigateModeHandler,
        "sync": SyncModeHandler,
    }

    def __init__(self, parent=None, video_window=None):
        plot_data = PlotData()
        # following two parts are necessary when initializing a plot
        plot_data.data = pd.DataFrame(data=[], columns=["time"])
        plot_data.annotations = dict()

        super().__init__(label_classes=[BaseRegionLabel], parent=parent, plot_data=plot_data)
        StateKeeper.video_duration_available.connect(self.update_video_duration)
        self.state = SensorPlotState()
        self.mode_handler = InvestigateModeHandler(self)
        self.state.bind(self._change_mode, "mode", initial_set=False)
        self.video_window = video_window

    def move_video_cursor_line(self, ev):  # pylint: disable=arguments-differ
        self.video_cursor_line.setValue(self.video_window.slider.value() / 1000)
        return ev

    def _change_mode(self, new_mode: MODES):
        """Adapt tool tip text depending on mode and remove potentially plotted green line indicating a new event.

        Parameters
        ----------
        new_mode
            One of `add`, `edit`, `remove`, or `investigate`
        """
        # Deactivate old mode_handler:
        self.mode_handler.deactivate()
        self.mode_handler = self.MODE_HANDLER[new_mode](self)
        self._set_tooltip(new_mode)

    def distribute_video_sync(self):
        # Better: we should bind the sync items region to the sync of the VideoWindow
        self.video_window.start = self.sync_item.getRegion()[0] * 1000  # needs it in milli-seconds
        self.video_window.end = self.sync_item.getRegion()[1] * 1000

    def _set_tooltip(self, mode: MODES):
        tips = {
            "sync": "Move the lines such that\n   - the green lines indicate moments at which all data streams are at "
        }
        tooltip = tips.get(mode, None)
        self.setToolTip(tooltip)

    def update_video_duration(self, length_seconds: float, fps: float):
        percentage = np.asarray([float(n) for n in range(0, 101)])
        x_values = percentage / 100 * length_seconds
        self.set_data(x=x_values, y=np.zeros(len(x_values)), fps=fps)

    def set_data(self, x: List, y: List, fps: Optional[float]):
        self.plot(x=x, y=y)
        self.plot_data = PlotData()
        self.plot_data.data = x
        if fps:
            self.plot_data.sampling_rate_hz = fps

    def add_sync_item(self):
        # just make sure we have the correct sampling frequency and video duration
        self.update_video_duration(self.video_window.player.duration(), self.video_window.fps)
        super().add_sync_item()
