from PySide2.QtCore import QObject, Qt, Slot
from PySide2.QtGui import QKeyEvent

from mad_gui.models.ui_state import PlotState
from typing import Optional, Tuple


def move_range(old_range: Tuple[float, float], distance: float, max_range: Tuple[float, float]) -> Tuple[float, float]:
    # TODO: Move to global helper
    if old_range[0] + distance < max_range[0]:
        return max_range[0], old_range[1] + (max_range[0] - old_range[0])
    if old_range[1] + distance > max_range[1]:
        return old_range[0] + (max_range[1] - old_range[1]), max_range[1]
    return old_range[0] + distance, old_range[1] + distance


class KeyEventHandler(QObject):
    """Used as a singleton to propagate key press events from children to :class:`mad_gui.windows.MainWindow`."""

    STATE_CHANGE = {
        Qt.Key_A: "add",
        Qt.Key_E: "edit",
        Qt.Key_R: "remove",
        Qt.Key_S: "sync",
        Qt.Key_I: "investigate",
        Qt.Key_Escape: "investigate",
    }

    def __init__(self, plot_state: PlotState, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.plot_state = plot_state

    @Slot(QKeyEvent)
    def key_pressed(self, event: QKeyEvent):
        self._global_mode_change_events(event)
        self._global_plot_move(event)

    def _global_mode_change_events(self, ev):
        new_mode = self.STATE_CHANGE.get(ev.key(), None)
        if new_mode:
            ev.accept()
            if new_mode == self.plot_state.mode:
                self.plot_state.mode = "investigate"
                return
            self.plot_state.mode = new_mode

    def _global_plot_move(self, ev):
        if ev.key() == Qt.Key_Q:
            old_range = self.plot_state.x_range
            jump_range = (old_range[1] - old_range[0]) * 0.8
            if ev.modifiers() == Qt.ShiftModifier:
                # move backwards
                self.plot_state.x_range = move_range(old_range, -jump_range, self.plot_state.x_range_max)
            else:
                # move forward
                self.plot_state.x_range = move_range(old_range, jump_range, self.plot_state.x_range_max)
            ev.accept()
