import numpy as np
import pyqtgraph as pg
from PySide2.QtGui import QColor, QHoverEvent, Qt

from mad_gui.components.dialogs.label_annotation_dialog import NestedLabelSelectDialog
from mad_gui.config import Config
from mad_gui.state_keeper import StateKeeper
from typing import Optional


class InvalidStartEnd(Exception):
    pass


class NoLabelSelected(Exception):
    pass


class BaseRegionLabel(pg.LinearRegionItem):
    """A label with a start and end plotted in the upper part of the graph.

    Parameters
    ----------
    label_id
        An id for the label. Usually we just give it an increasing number.
    label_type
        Filled, when :meth:`~RegionLabel.edit_activity_type` triggers
        :meth:`mad_gui._StateKeeper.need_label_description`.
    label_details
        Similar like label_type. Additionally it is configurable for which label types details should be obtained and
        what the possible options for details are. For more information on this see docs/consts_example.
    start
        Start time of the label in samples.
    end
        End time of the label in samples.
    parent
        A :class:`mad_gui.plot_tools.BasePlot` object.

    """

    min_height = 0
    max_height = 1
    color = [100, 100, 100, 50]
    name = "Label"

    def __init__(
        self,
        start: int,
        end: int,
        parent,
        identifier: int = None,
        description: Optional[str] = None,
        details: Optional[str] = None,
        **_kwargs,  # underscore to prevent pylint form triggering
    ):
        pg.LinearRegionItem.__init__(self)
        self.parent = parent
        self.setMovable(False)
        self._set_border_colors(start, end)
        self._set_border_positions(start, end)
        self.configure_children()
        self.standard_brush = pg.mkBrush(QColor(*self.color))
        self.sigRegionChangeFinished.connect(self._region_changed)
        self._set_movable(True)
        if start == end:
            return
        self.id = identifier
        self.description = description
        self.details = details
        # TODO: put the next few lines into a function like `set_start_colors`, which can be overwritten by
        #  StrideLabels. Reason: StrideLabels should be initialized with blue borders, but activities should be
        #  initialized with red borders.
        self.configure_children()
        self.span = (self.min_height, self.max_height)

        # The stride itself as a whole should not be movable, just the single lines (children = InfiniteLines)
        self.setAcceptHoverEvents(True)

        self.setBrush(self.standard_brush)
        self.mouseClickEvent = self._left_mouse_click_event
        self.removable = False
        self.editable = False
        self._set_movable(False)
        self.hoverEvent = self._hover_event
        if self.description:
            self.setToolTip(", ".join(self.description))

    def _left_mouse_click_event(self, ev):
        if self.removable and ev.button() == Qt.LeftButton:
            # TODO: create a signal "i want to be deleted" and let the parent delete it
            self.parent.removeItem(self)
            StateKeeper.set_has_unsaved_changes(True)
        elif self.editable and ev.button() == Qt.LeftButton:
            self.edit_activity_type()

    def _hover_event(self, ev):
        """Coloring if mouse hovers of the stride"""
        # first of all, make sure the current stride is in the foreground, s.t. when mouse click event happens to
        # change the range, the mouse click event captures this stride's borders and not the neighbouring stride which
        # might have been plotted after this one originally and therefore might have been in the foreground
        self.parent.removeItem(self)
        self.parent.addItem(self)

        if self.removable:
            hover_color = QColor(255, 0, 0, 50)
        else:
            hover_color = QColor(0, 255, 0, 50)
        self.setHoverBrush(hover_color)
        if self.removable or self.editable:
            if ev.enter:
                self.setMouseHover(True)
            if ev.exit:
                self.setMouseHover(False)
                self.setHoverBrush(self.standard_brush)
        # TODO: this is not properly handled when calling self.edit_activity_type --> fix it
        self.setToolTip(f"{self.description}")

    def edit_activity_type(self):
        """Setting the type of the activity to one given in the consts file.

        Called by :meth:`mad_gui.plot_tools.SensorPlot._finish_adding_activity` or if the user clicks on the label while
        being in edit mode. The emitted signal is caught by :meth:`mad_gui.MainWindow.ask_for_label_type`. In case
        the configuration file is configured in a way, that also details should be obtained for specific activity types,
        this will be triggered after obtaining the label type.

        For further information on the configuration file, see `Developer Guidelines
        <https://madlab.mad-pages.informatik.uni-erlangen.de/GaitAnalysis/labeling_tool/developer_guidelines.html#
        adding-support-for-other-systems>`_

        """
        new_description = NestedLabelSelectDialog(parent=self.parent.parent).get_label(Config.settings.ACTIVITIES)
        if not new_description:
            raise NoLabelSelected("Invalid description selected for label")
        self.description = new_description

    def _set_removable(self, removable: bool):
        self.removable = removable
        if not removable:
            self.setBrush(self.standard_brush)

    def _set_editable(self, editable: bool):
        self.editable = editable

    def _set_movable(self, movable: bool):
        for i_child in self.childItems():
            i_child.setMovable(movable)

    def make_editable(self):
        self._set_removable(False)
        self._set_editable(True)
        self._set_movable(True)

    def make_removable(self):
        self._set_removable(True)
        self._set_editable(False)
        self._set_movable(False)

    def make_readonly(self):
        self._set_removable(False)
        self._set_editable(False)
        self._set_movable(False)

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
        # TODO: change brush
        StateKeeper.set_has_unsaved_changes(True)

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
