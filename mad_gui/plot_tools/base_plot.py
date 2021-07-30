"""This module keeps all the base classes for mad_gui.plot_tools."""
import pandas as pd
import pyqtgraph as pg
from pyqtgraph.GraphicsScene.mouseEvents import MouseClickEvent
from PySide2.QtCore import Slot
from PySide2.QtGui import QColor, QCursor, QMouseEvent

from mad_gui.config import Config
from mad_gui.plot_tools.base_label import BaseLabel
from typing import Optional


class BasePlot(pg.PlotWidget):
    """A base plot that can display data and additionally show a yellow line to indicate the current position in a
    video."""

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent=None)
        self.parent = parent
        self.configure_style()
        self.video_cursor_line = None
        self.cursor_line_pen = pg.mkPen(color="y", width=3)
        self.sync_item = None
        self.sync_info = None

    def set_title(self, title: str):
        """Set the title, which will be shown centered on the top of the plot.

        Parameters
        ----------
        title
            The title that should be shown on the top of the plot.

        """
        self.setTitle(title)
        self.plotItem.titleLabel.setText(text=title, color=Config.theme.FAU_COLORS["dark_blue"])

    def configure_style(self):
        self.setBackground(Config.theme.FAU_COLORS["medium_blue"])
        for i_channel in ["bottom", "left"]:
            self._adapt_channel_color(i_channel, Config.theme.FAU_COLORS["dark_blue"])

    def _adapt_channel_color(self, channel: str, color: QColor):
        """Make channel color in FAU style"""
        ax = self.getAxis(channel)
        ax.setPen(color=color)
        ax.setTextPen(color=color)

    def set_coupled_plot(self, other: Optional[pg.PlotWidget] = None):
        """Couple another plot to this one, such that both plots always have the same x- and y- limits.

        Parameters
        ----------
        other
            Usually another object of :class:`~mad_gui.plot_tools.SensorPlot`.
        """
        if getattr(Config.settings, "SENSORS_SYNCHRONIZED", False):
            self.setXLink(other)
        if getattr(Config.settings, "BIND_Y_AXIS", False):
            self.setYLink(other)

    def enterEvent(self, ev):  # noqa
        # Camelcase method overwrites qt method
        self.setFocus()
        return super().enterEvent(ev)

    def inside_plot_range(self, local_pos):
        x_min = self.viewRange()[0][0]
        x_max = self.viewRange()[0][1]
        y_min = self.viewRange()[1][0]
        y_max = self.viewRange()[1][1]
        if x_min < local_pos.x() < x_max and y_min < local_pos.y() < y_max:
            return True
        return False

    def get_mouse_pos_from_event(self, ev):
        if isinstance(ev, QMouseEvent):
            position = ev.localPos()
        elif isinstance(ev, MouseClickEvent):
            position = ev.scenePos()
        else:
            # Keyboard events or others
            position = self.mapFromGlobal(QCursor.pos())
        return self.plotItem.vb.mapSceneToView(position)

    def add_video_cursor_line(self, pos: int = None):
        """Add a line that shows to which sample in the signal the currently shown video frame corresponds.

        Parameters
        ----------
        pos
            Position at which the line should be shown (in seconds)
        """
        if pos is None:
            x_range = self.viewRange()[0][1] - self.viewRange()[0][0]
            pos = self.viewRange()[0][0] + x_range / 2
        if not self.video_cursor_line:
            self.video_cursor_line = pg.InfiniteLine(pos=pos, angle=90, name="vertical_line", pen=self.cursor_line_pen)
            self.addItem(self.video_cursor_line)

    def remove_video_cursor_line(self):
        """Remove the line that indicates video-signal correspondence when the video window is closed."""
        if self.video_cursor_line:
            self.removeItem(self.video_cursor_line)
            self.video_cursor_line = None

    def _percent_to_position(self, percent_since_start: float):
        if self.plot_data.data is None:
            return 0
        if self.sync_info is None or any(pd.isna(self.sync_info)):
            x_axis = self.plotItem.listDataItems()[0].getData()[0]
            sec = percent_since_start / 100 * x_axis[-1]
        else:
            stream_length = (self.sync_info["end"] - self.sync_info["start"]) / self.plot_data.sampling_rate_hz
            sec = self.sync_info["start"] / self.plot_data.sampling_rate_hz + stream_length * percent_since_start / 100
        return sec

    def move_video_cursor_line(self, percent_since_start: float):
        """Move the line that indicates to which signal sample the current video frame corresponds.

        Parameters
        ----------
        percent_since_start
            the percentage of the data stream to jump to since start
        """
        if self.video_cursor_line:  # otherwise this causes an error during testing
            sec = self._percent_to_position(percent_since_start)
            self.video_cursor_line.setValue(sec)

    @Slot(int)
    def set_graph_position(self, percent_since_start: float):
        """Move the graph such that `sample` is in the middle of the plot.

        Parameters
        ----------
        percent_since_start
            the percentage of the data stream to jump to since start

        """
        if self.state.mode == "sync":
            return
        sec = self._percent_to_position(percent_since_start)
        x_min = sec - Config.settings.PLOT_WIDTH_PLAYING_VIDEO * 0.5
        x_max = sec + Config.settings.PLOT_WIDTH_PLAYING_VIDEO * 0.5
        self.setXRange(x_min, x_max)

    def finish_syncing(self):
        if self.sync_item:
            start_sample = self.sync_item.getRegion()[0] * self.plot_data.sampling_rate_hz
            end_sample = self.sync_item.getRegion()[1] * self.plot_data.sampling_rate_hz
            self.sync_info = pd.Series(data=[start_sample, end_sample], index=["start", "end"])
            self._remove_sync_item()
        self.add_video_cursor_line()

    def add_sync_item(self):
        if self.sync_item:
            self.autoRange()
            return
        if self.plot_data.data is None:
            return
        if self.sync_info is None:
            start = self.viewRange()[0][0]
            end = self.viewRange()[0][1]
            x_range = end - start
            self.sync_item = SynchronizationLabel(
                start=(start + 0.1 * x_range) * self.plot_data.sampling_rate_hz,
                end=(end - 0.1 * x_range) * self.plot_data.sampling_rate_hz,
                parent=self,
            )
        else:
            self.sync_item = SynchronizationLabel(
                start=self.sync_info.start,
                end=self.sync_info.end,
                parent=self,
            )
        self.addItem(self.sync_item)
        self.autoRange()

    def _remove_sync_item(self):
        self.removeItem(self.sync_item)
        self.sync_item = None


class SynchronizationLabel(BaseLabel):
    def __init__(self, start, end, parent=None):
        super().__init__(start, end, parent=parent)

    def _set_border_colors(self, start, end):
        self.start_color = QColor(0, 255, 0, 255)
        self.end_color = QColor("red")

    def _region_changed(self):
        """Called as soon as user drags start / end of a stride"""
        return
