import numpy as np
import pyqtgraph as pg
from PySide2.QtGui import QColor, QHoverEvent, Qt

from mad_gui.config import Config


class BaseLabel(pg.LinearRegionItem):
    """Used to manually synchronize different data streams by the user.

    Parameters
    ----------
    start
        Start time of the label in samples
    end
        End time of the label in samples
    parent
        A :class:`mad_gui.plot_tools.BasePlot` object.

    """

    def __init__(
        self,
        start: int,
        end: int,
        parent,
    ):
        pg.LinearRegionItem.__init__(self)
        self.parent = parent
        self.min_height = 0
        self.max_height = 1
        self.setMovable(False)
        self._set_border_colors(start, end)
        self._set_border_positions(start, end)
        self.configure_children()
        self.sigRegionChangeFinished.connect(self._region_changed)
        self._set_movable(True)

    def _set_movable(self, movable: bool):
        for i_child in self.childItems():
            i_child.setMovable(movable)

    def _set_border_positions(self, start, end):
        sampling_rate_hz = self.parent.plot_data.sampling_rate_hz
        if np.isnan(start):
            start = end - 1.5 * sampling_rate_hz
        if np.isnan(end):
            end = start + 1.5 * sampling_rate_hz
        self.setRegion(
            (
                start / sampling_rate_hz,
                end / sampling_rate_hz,
            )
        )

    def _set_border_colors(self, start, end):
        """Color-code start and end of the label.

        It may happen that either the start or the end of a label is `None`. This can happen for example,
        when :func:`~mad_gui.plugins.BaseImporter.load_activity_stride_annotation_list` (or actually your
        implementation of it) finds a start for some activities but no end. This happens for example in the context of
        gait analysis, when a swing phase is found but no preceding stance phase - then there is no label of the start
        of the stride, but a label for terminal contact and the end of the stride.

        Color codes:
        red: The border is `None` and the user has to set it before saving evaluating. In case the user does not do
        that the event gets assigned to the red position before exporting data.
        orange: Either the user has not adapted the label and does not need to adapt it since loading was successful
        or the user has not dragged the lines after adding the label.
        blue: The user has adapted  the label successfully.

        Parameters
        ----------
        start
            Start time in samples
        end
            End time in samples
        """
        self.start_color = QColor("orange")
        self.end_color = QColor("orange")
        if np.isnan(start):
            self.start_color = QColor("red")
        if np.isnan(end):
            self.end_color = QColor("red")

    def configure_children(self):
        child_counter = 0
        for i_child in self.childItems():
            # make cursor horizontal when hovering
            i_child.hoverEvent = self._hover_border_event
            i_child.span = (self.min_height, self.max_height)
            # color of gait event lines
            if child_counter == 0:
                if self.start_color == QColor("red"):
                    width = 2
                else:
                    width = 1
                i_child.setPen(self.start_color, width=width)
            if child_counter == 1:
                if self.end_color in [QColor("red"), QColor("green")]:
                    width = 2
                else:
                    width = 1
                i_child.setPen(self.end_color, width=width)

            child_counter = child_counter + 1
            # make gait events (InfiniteLines) movable
            i_child.sigPositionChanged.connect(self._reposition_lines)
            i_child.setMovable(False)

    def _reposition_lines(self):
        fs = self.parent.plot_data.sampling_rate_hz
        for i_child in self.childItems():
            snapped_position = round(i_child.pos()[0] * fs) / fs
            i_child.setPos(snapped_position)

    def _region_changed(self):
        """Called as soon as user drags start / end of a stride"""
        # border might have been red in the beginning, set it to blue if user has corrected this
        for i_child in self.childItems():
            if i_child.pen.color() == QColor("red"):
                # This gait event was 'None' before and therefore marked red. Apparently the user shifted it,
                # so we think it is now at the correct position
                i_child.pen.setColor(Config.theme.FAU_COLORS["dark_blue"])

    def _hover_border_event(self, event: QHoverEvent):
        """Actions when hovering over the child item of type `pyqtgraph.InfiniteLine`"""
        mode = self.parent.state.mode
        if mode in ["edit", "sync"]:
            if event.enter:
                self.parent.setCursor(Qt.SizeHorCursor)
            if event.exit and mode == "edit":
                self.parent.setCursor(Qt.PointingHandCursor)
            elif event.exit:
                self.parent.setCursor(Qt.ArrowCursor)
