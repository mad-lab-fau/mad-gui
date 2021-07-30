import numpy as np
import pandas as pd
import pyqtgraph as pg
from PySide2.QtGui import QBrush, QColor, QLinearGradient, Qt
from PySide2.QtWidgets import QWidget

from mad_gui.config import Config
from mad_gui.plot_tools.base_label import BaseRegionLabel, InvalidStartEnd
from mad_gui.state_keeper import StateKeeper
from typing import Callable, Optional, Type


class SegmentedStrideLabel(BaseRegionLabel):
    """Stride labels that only have a start and an end.

    This class can for example be used to generate stride labels as suggested by Barth et al. [1]_. This label looks
    like an :class:`RegionLabel`, just that it is placed in the area of `MIN_HEIGHT_STRIDE_LABELS` to
    `MAX_HEIGHT_STRIDE_LABELS`. Furthermore, its start and end can snap to minima by setting STRIDE_SNAP_TO_MIN
    (see `docs/consts_example.md`).

    .. [1] Barth, J., Oberndorfer, C., Kugler, P., Schuldhaus, D., Winkler, J., Klucken, J., & Eskofier, B. (2013).
       Subsequence dynamic time warping as a method for robust step segmentation using gyroscope signals of daily life
       activities. Proceedings of the Annual International Conference of the IEEE Engineering in Medicine and Biology
       Society, EMBS, 6744–6747. https://doi.org/10.1109/EMBC.2013.6611104

    See Also
    --------
    :class:`RegionLabel`

    """

    def __init__(self, identifier: int, start: int, end: int, parent, **_kwargs):
        super().__init__(identifier, start, end, parent)
        self.min_height = Config.settings.MIN_HEIGHT_STRIDE_LABELS
        self.max_height = Config.settings.MAX_HEIGHT_STRIDE_LABELS
        self.span = (self.min_height, self.max_height)
        self.configure_children()
        self.standard_brush = StrideLabel._generate_brush(self)  # --> RegionLabel
        self.setBrush(self.standard_brush)


class StrideLabel(BaseRegionLabel):
    """Stride labels that have a start, an end, and a terminal contact event.

    Parameters
    ----------
    events
        A pandas series, where the indexes are the event names (like for example `tc`) and the values are the event
        position in samples. Up to now we only support a the event `tc`.

    See Also
    --------
    :class:`RegionLabel`

    """

    def __init__(
        self,
        identifier: int,
        start: int,
        end: int,
        parent,
        events: Optional[pd.Series] = None,
        description: Optional[str] = None,
        details: Optional[str] = None,
    ):
        # TODO: transform tc into a list of gait events
        super().__init__(
            start=start, end=end, parent=parent, identifier=identifier, description=description, details=details
        )
        self.min_height = Config.settings.MIN_HEIGHT_STRIDE_LABELS
        self.max_height = Config.settings.MAX_HEIGHT_STRIDE_LABELS
        self.span = (self.min_height, self.max_height)
        self.configure_children()
        self.tc_color = Config.theme.FAU_COLORS["dark_blue"]
        if events is not None:
            tc = events.tc
            if np.isnan(tc):
                tc = end - 0.1 * self.parent.sampling_rate_hz
                self.tc_color = QColor("red")
            self._add_tc_event(tc / self.parent.sampling_rate_hz)
        # make data lines stay in foreground
        self.setFlag(self.ItemStacksBehindParent, True)
        self.standard_brush = self._generate_brush()
        self.setBrush(self.standard_brush)

    def _generate_brush(self):
        grad = QLinearGradient(self.getRegion()[0], 0, self.getRegion()[1], 0)
        grad.setColorAt(0, QColor(0, 0, 255, 100))
        grad.setColorAt(0.6, QColor(0, 0, 255, 50))
        grad.setColorAt(1, QColor(0, 0, 255, 0))
        return QBrush(grad)

    def _add_tc_event(self, tc_pos: float):
        """Adding a terminal contact to the stride label visualization.

        Parameters
        ----------
        tc_pos
            x-coordinate in seconds

        # TODO: Change signature s.t. it accepts an event to be consistent in SensorPlot._add_label_mouse_move_event()
        """
        tc = pg.InfiniteLine(
            pos=tc_pos,
            movable=True,
            pen=pg.mkPen(style=Qt.DashLine, color=QColor(0, 0, 0, 255)),
        )
        tc.span = (
            Config.settings.MIN_HEIGHT_STRIDE_LABELS,
            Config.settings.MAX_HEIGHT_STRIDE_LABELS,
        )
        stride_region = self.getRegion()
        tc.setParentItem(self)
        tc.setBounds(stride_region)
        self.lines.append(tc)
        self.configure_children()

    def _tc_pos_changed(self):
        fs = self.parent.sampling_rate_hz
        snapped_position = round(self.tc.pos()[0] * fs) / fs
        self.tc.setPos(snapped_position)
        StateKeeper.set_has_unsaved_changes(True)

    def _left_mouse_click_event(self, ev):
        if self.removable and ev.button() == Qt.LeftButton:
            self.parent.removeItem(self)

    def _region_changed(self):
        BaseRegionLabel._region_changed(self)
        stride_region = self.getRegion()
        self.lines[2].setBounds((stride_region[0] + 0.03, stride_region[1] - 0.03))
        self.setBrush(self._generate_brush())


# TODO: Change so that start and end are in the same coordinate system as the other labels
class PartialLabel(pg.LinearRegionItem):
    """Wrap a label instance during creation"""

    def __init__(
        self,
        raw_start,
        sampling_rate_hz: float,
        label_class: Type[BaseRegionLabel],
        label_id: int,
        label_parent: Optional[QWidget] = None,
        post_process: Optional[Callable] = None,
    ):
        self.sampling_rate_hz = sampling_rate_hz
        self.label_class = label_class
        self.label_id = label_id
        self.label_parent = label_parent
        self.post_process = post_process
        start = raw_start
        if post_process is not None:
            start = post_process(raw_start)
        super(PartialLabel, self).__init__(
            values=(start, start),
            pen=pg.mkPen(Config.theme.FAU_COLORS["dark_blue"]),
            swapMode="block",
        )
        self.span = (label_class.min_height, label_class.max_height)
        for i_child in self.childItems():
            i_child.span = self.span
        self.line_style = Qt.SolidLine
        if self.label_class is StrideLabel:
            self.line_style = Qt.DashLine

        self.setMovable(False)
        self.sigRegionChangeFinished.connect(self.on_range_change)

    def on_range_change(self):
        # Adapt color based on label class
        color = QColor(0, 255, 0)
        children = self.childItems()
        children[-1].setPen(pg.mkPen(color=color, style=self.line_style, width=2))

    def update_end(self, new_end):
        current_region = self.getRegion()
        new_region = (current_region[0], new_end)
        self.setRegion(new_region)

    def finalize(self):
        start, end = self.getRegion()
        if self.post_process is not None:
            end = self.post_process(end)

        if start == end:
            raise InvalidStartEnd()
        final_label = self.label_class(
            identifier=self.label_id,
            start=start * self.sampling_rate_hz,
            end=end * self.sampling_rate_hz,
            parent=self.label_parent,
        )
        if self.label_class == BaseRegionLabel:
            # If it is an activity label, we need to select the activity type
            final_label.edit_activity_type()
        return final_label


class SynchronizationLabel(BaseRegionLabel):
    def __init__(self, start, end, parent=None):
        super().__init__(start=start, end=end, parent=parent)

    def _set_border_colors(self, start, end):
        self.start_color = QColor(0, 255, 0, 255)
        self.end_color = QColor("red")

    def _region_changed(self):
        return

    def _left_mouse_click_event(self, ev):
        pass

    def _hover_event(self, ev):
        pass


# stride_label_config = {"segmented_stride": SegmentedStrideLabel, "stride": StrideLabel}
