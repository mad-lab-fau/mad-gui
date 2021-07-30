from __future__ import annotations

from pyqtgraph import InfiniteLine, mkPen
from PySide2.QtCore import Qt

from mad_gui.components.dialogs.user_information import UserInformation
from mad_gui.config import Config
from mad_gui.plot_tools.base_label import BaseRegionLabel, InvalidStartEnd, NoLabelSelected
from mad_gui.plot_tools.base_mode_handler import BaseModeHandler
from mad_gui.plot_tools.labels import PartialLabel
from typing import Optional, Type


class AddModeHandler(BaseModeHandler):
    mode = "add"
    _partial_label: Optional[PartialLabel] = None
    _potential_start: Optional[InfiniteLine] = None

    def __init__(self, sensor_plot):
        super().__init__(plot=sensor_plot)

    def handle_mouse_click(self, ev):
        # If no active label, create new stride -> switch to edit mode
        mouse_position = self.plot.get_mouse_pos_from_event(ev)
        if self.plot.inside_label_range(mouse_position):
            self._add_label_at_mouse_pos(mouse_position)
        else:
            super().handle_mouse_click(ev)
        ev.accept()

    def handle_key_press(self, ev):
        """In add mode we handle spacebar and esc.

        If spacebar is pressed we add a new label or finalize it (like with mouse click.
        Esc removes a label that is curretnly added
        """
        key = ev.key()
        if key == Qt.Key_Space:
            local = self.plot.get_mouse_pos_from_event(ev)
            self._add_label_at_mouse_pos(local)
            if self._partial_label is None and ev.modifiers() == Qt.ShiftModifier:
                # If we press Shift+Space we directly create a new event if one is finished
                self._add_label_at_mouse_pos(local)
            ev.accept()
            return
        if key == Qt.Key_Escape:
            self._clear_partial_label()
            ev.accept()
            return
        super().handle_key_press(ev)

    def handle_mouse_movement(self, ev):
        if self._partial_label is None or not self.plot.inside_plot_range(self.plot.get_mouse_pos_from_event(ev)):
            self._reposition_potential_start(ev)
            super(AddModeHandler, self).handle_mouse_movement(ev)
            return
        pos = self.plot.get_mouse_pos_from_event(ev)
        self._reposition_new_end(pos)
        ev.accept()

    def deactivate(self):
        self._clear_partial_label()

    def _add_label_at_mouse_pos(self, pos):
        plot = self.plot
        # is called when in "Add Label" Mode and user clicks mouse
        label_class = plot.inside_label_range(pos)
        if not label_class:
            return
        if self._partial_label is not None and self._partial_label.label_class is label_class:
            self._finalize_new_label()
            return

        # In case we started a label of another type, we clean it just to be sure
        # TODO: This might be a dumn idea, as this will delete your partial label, if you click in the wrong region
        self._clear_partial_label()
        self._start_new_label(pos, label_class)

    def _start_new_label(self, pos, label_class: Type[BaseRegionLabel]):
        plot = self.plot
        label_class = self.plot.inside_label_range(pos)
        if getattr(label_class, "snap_to_min", False):
            post_process = plot.snap_to_min
        else:
            post_process = plot.snap_to_sample

        if self._partial_label:
            self._clear_partial_label()
        self._partial_label = PartialLabel(
            raw_start=pos.x(),
            sampling_rate_hz=plot.plot_data.sampling_rate_hz,
            label_class=label_class,
            label_id=plot._get_appropriate_stride_id(),
            label_parent=plot,
            post_process=post_process,
        )
        # TODO: adapt this to add new gait events as long as a list of gait events in new_stride (which does not
        #  exist yet) does not have the number of elements as plot.get_stride_list.drop_columns(["start",
        #  "end"]).columns has
        # plot.new_stride.tc = None
        plot.addItem(self._partial_label)

    def _finalize_new_label(self):
        plot = self.plot
        if self._partial_label is None:
            raise ValueError("No label to finish")
        try:
            new_label = self._partial_label.finalize()
        except InvalidStartEnd:
            UserInformation(parent=plot.parent).inform("New Label has length 0. No new label added.")
            return
        except NoLabelSelected:
            # In cas ethe user opened the label selector, but closed it again, we assume that opening was an accident
            # and allow the user to further modify the label
            return
        plot.addItem(new_label)
        self._clear_partial_label()

    def _reposition_new_end(self, pos):
        pos = self.plot.snap_to_sample(pos.x())
        self._partial_label.update_end(pos)

    def _reposition_potential_start(self, ev):
        pos = self.plot.get_mouse_pos_from_event(ev)
        snapped_pos = self.plot.snap_to_sample(pos.x())
        if self._potential_start:
            self.plot.removeItem(self._potential_start)

        label_class = self.plot.inside_label_range(pos)
        if label_class:
            self._potential_start = InfiniteLine(snapped_pos, pen=mkPen(0, 255, 0, 150, width=2))
            self._potential_start.span = (
                label_class.min_height,
                label_class.max_height,
            )
            self.plot.addItem(self._potential_start)

    def _clear_partial_label(self):
        if self._partial_label is not None:
            self.plot.delete_item(self._partial_label)
            self._partial_label = None


class InvestigateModeHandler(BaseModeHandler):
    mode = "investigate"

    def __init__(self, sensor_plot):
        super().__init__(plot=sensor_plot)

    def deactivate(self):
        pass


class EditModeHandler(BaseModeHandler):
    def __init__(self, sensor_plot):
        super().__init__(sensor_plot)

        for item in self.plot.items():
            if isinstance(item, BaseRegionLabel):
                item.make_editable()

    def deactivate(self):
        for item in self.plot.items():
            if isinstance(item, BaseRegionLabel):
                item.make_readonly()


class RemoveModeHandler(BaseModeHandler):
    def __init__(self, sensor_plot):
        super().__init__(sensor_plot)

        for item in self.plot.items():
            if isinstance(item, BaseRegionLabel):
                item.make_removable()

    def deactivate(self):
        for item in self.plot.items():
            if isinstance(item, BaseRegionLabel):
                item.make_readonly()


class SyncModeHandler(BaseModeHandler):
    def __init__(self, sensor_plot):
        super().__init__(sensor_plot)
        self.plot.remove_video_cursor_line()
        sensors_synced = hasattr(Config.settings, "SENSORS_SYNCHRONIZED") and Config.settings.SENSORS_SYNCHRONIZED
        if self.plot.is_main_plot or not sensors_synced:
            self.plot.add_sync_item()
        if not (hasattr(Config.settings, "SENSORS_SYNCHRONIZED") and Config.settings.SENSORS_SYNCHRONIZED):
            self.plot.set_coupled_plot(None)
        else:
            # TODO: only create a sync item in the main plot --> remove in other plot(s) since it gets generated
            #  automatically
            pass

        for item in self.plot.items():
            if isinstance(item, BaseRegionLabel):
                item.make_editable()

    def deactivate(self):
        self.plot.finish_syncing()
        for item in self.plot.items():
            if isinstance(item, BaseRegionLabel):
                item.make_readonly()
