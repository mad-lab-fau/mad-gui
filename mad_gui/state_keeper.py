"""Keeps the state of the GUI and related signals / slots."""

from PySide2.QtCore import QObject, Signal, Slot


class _StateKeeper(QObject):
    """Used as a singleton to enable communication between objects that don't have a direct relationship.

    In the section `Other Parameters`, all Signals are listed. You can emit a certain signal by calling
    `StateKeeper.<signal name>.emit(<potential arguments, like a text>). Slots are listed as Methods and you can
    connect to them like this: `StateKeeper.<slot name>.connect(<the method you want to call upon emission of that
    signal>).

    Attributes
    ----------
    current_frame
        The frame that is shown by :class:`mad_gui.VideoWindow`
    label_state
        One of the states "add", "remove", "edit", or "investigate". State information is color-coded by the buttons
        in the
        upper part of the GUI. Can be changed by mouse-click or shortcuts "a", "e", or "Esc".
    gui_has_unsaved_changes
        Keeps information if there has been any user interaction since last time data was either exported using
        :meth:`mad_gui.MainWindow._export` or saved using :meth:`mad_gui.MainWindow._save_data_gui_format`.

    """

    announce_data_types = Signal(dict)  # MainWindow / DataSelector

    save_sync = Signal()

    data_position_changed = Signal(float)
    video_window_closed = Signal()
    video_duration_available = Signal(float, float)
    gui_has_unsaved_changes = False
    plugins = []

    @Slot(int)
    def frame_changed(self, frame: int):
        self.signal_sample_changed.emit(self.synchronizer.frame_to_sample(frame))
        self.signal_frame_changed.emit(frame)

    @Slot(bool)
    def set_has_unsaved_changes(self, flag: bool):
        self.gui_has_unsaved_changes = flag


StateKeeper = _StateKeeper()
