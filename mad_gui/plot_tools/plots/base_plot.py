"""This module keeps all the base classes for mad_gui.plot_tools."""
import pandas as pd
import pyqtgraph as pg
from pyqtgraph.GraphicsScene.mouseEvents import MouseClickEvent
from PySide2.QtCore import Slot
from PySide2.QtGui import QColor, QCursor, QMouseEvent, QPalette

from mad_gui.config import Config
from mad_gui.models.local import AnnotationData, PlotData
from mad_gui.plot_tools.labels import SynchronizationLabel
from mad_gui.plot_tools.labels.base_label import BaseEventLabel, BaseRegionLabel
from typing import List, Optional, Type


class BasePlot(pg.PlotWidget):
    """A base plot that can display data and additionally show a yellow line to indicate the current position in a
    video."""

    def __init__(
        self,
        plot_data: PlotData = None,
        initial_plot_channels=None,
        label_classes: List[BaseRegionLabel] = None,
        event_classes: Optional[List[BaseEventLabel]] = None,
        parent=None,
    ):
        super().__init__(parent=None)
        self.parent = parent
        self.plot_data = plot_data
        self.label_classes = label_classes
        self.event_classes = event_classes
        self.initial_plot_channels = initial_plot_channels or list(plot_data.data.columns)
        self.configure_style()
        self.video_cursor_line = None
        self.cursor_line_pen = pg.mkPen(color="y", width=1)
        self.sync_item = None
        self.sync_info = None
        self.label_ranges = None
        self.event_ranges = None
        self.event_labels = {}
        self._initialize_labels(label_classes)
        self._initialize_events(event_classes)

    def _initialize_events(self, event_classes: List):
        # if not hasattr(self.plot_data.annotations, "events"):
        #    return
        # df = self.plot_data.annotations["events"].data
        # for _, event in df.iterrows():
        #    pos = self.snap_to_sample(event.pos / self.plot_data.sampling_rate_hz)
        #    self.addItem(BaseEventLabel(pos=pos, span=(event.min_height, event.max_height), parent=self))
        if event_classes is None:
            return
        event_ranges = pd.DataFrame()
        for event_class in event_classes:
            if event_class.name not in self.plot_data.annotations.keys():
                self.plot_data.annotations[event_class.name] = AnnotationData()
            self.set_events(event_class, self.plot_data.annotations[event_class.name].data)
            event_range = pd.DataFrame(
                index=[event_class.name],
                data=[[event_class.min_height, event_class.max_height]],
                columns=["min_height", "max_height"],
            )
            event_ranges = event_ranges.append(event_range)
        self.event_ranges = event_ranges

    def _initialize_labels(self, labels: List):
        label_ranges = pd.DataFrame()

        for label_class in labels:
            if label_class.name not in self.plot_data.annotations.keys():
                self.plot_data.annotations[label_class.name] = AnnotationData()

            self.set_labels(label_class, self.plot_data.annotations[label_class.name].data)

            label_range = pd.DataFrame(
                index=[label_class.name],
                data=[[label_class.min_height, label_class.max_height]],
                columns=["min_height", "max_height"],
            )
            label_ranges = label_ranges.append(label_range)
        self.label_ranges = label_ranges

    @Slot(BaseEventLabel, pd.DataFrame)
    def set_events(self, label_class: Type[BaseEventLabel], df: pd.DataFrame):
        if df is None or df.empty:
            return
        self.clear_labels(label_class)
        for _, event in df.iterrows():
            new_event = label_class(
                pos=event.position,
                description=event.description,
                parent=self,
            )
            self.addItem(new_event)

    @Slot(BaseRegionLabel, pd.DataFrame)
    def set_labels(self, label_class: Type[BaseRegionLabel], df: pd.DataFrame):
        if df is None or df.empty:
            return
        self.clear_labels(label_class)
        for _, activity in df.iterrows():
            # make sure there are no np.nans in any string field
            mask = activity.index.isin(["start", "end"])
            activity[~mask] = activity[~mask].fillna("")
            necessary_columns = ["identifier", "description", "events"]
            # events = getattr(label_class, "events", None)
            # if events:
            #    necessary_columns.extend(events)

            # make sure all required fields are available
            for parameter in necessary_columns:
                if parameter not in activity.index:
                    activity = activity.append(pd.Series(data=[None], index=[parameter]))
            if hasattr(label_class, "events"):
                events = activity[label_class.events]
            else:
                events = None
            new_activity = label_class(
                identifier=activity.identifier,
                description=activity.description,
                start=activity.start,
                end=activity.end,
                events=events,
                parent=self,
            )
            self.addItem(new_activity)
            for event in new_activity.event_labels.values():
                self.addItem(event)

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
        bg_color = Config.theme.COLOR_LIGHT
        self.setBackground(bg_color)
        for i_channel in ["bottom", "left"]:
            self._adapt_channel_color(i_channel, self.parent.palette().color(QPalette.Active, QPalette.Window))

    def _adapt_channel_color(self, channel: str, color: QColor):
        """Make channel color in FAU style"""
        ax = self.getAxis(channel)
        ax.setPen(color=color, width=1)
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

    def _inside_range(self, pos, label_ranges: pd.DataFrame):
        for label_name, label_range in label_ranges.iterrows():

            y_min = self.viewRange()[1][0]
            y_max = self.viewRange()[1][1]

            if label_range.min_height <= (pos.y() - y_min) / (y_max - y_min) <= label_range.max_height:
                return label_name
        return None

    def inside_event_range(self, pos):
        if self.event_ranges.empty:
            return None
        return self._get_event_class(self._inside_range(pos, self.event_ranges))

    def inside_label_range(self, pos):
        return self._get_label_class(self._inside_range(pos, self.label_ranges))

    def _get_event_class(self, event_name: str):
        for label in self.event_classes:
            if label.name == event_name:
                return label
        return None

    def _get_label_class(self, label_name: str):
        for label in self.label_classes:
            if label.name == label_name:
                return label
        return None

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

    def snap_to_sample(self, pos: float):
        sampling_rate_hz = self.plot_data.sampling_rate_hz
        # make at least sure it is at the position of an actual sample
        return round(pos * sampling_rate_hz) / sampling_rate_hz

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
        x_min = sec - getattr(Config.settings, "PLOT_WIDTH_PLAYING_VIDEO", 20) * 0.5
        x_max = sec + getattr(Config.settings, "PLOT_WIDTH_PLAYING_VIDEO", 20) * 0.5
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
