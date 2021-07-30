from PySide2.QtCore import QObject, QPropertyAnimation, Signal


class Sidebar(QObject):
    """This is not a real sidebar implementation, but just a logic wrapper.

    I would be better to actual use this as widget component, but we would need to change the UI for this.
    """

    def __init__(self, ui, parent=None, initial_collapsed: bool = False):
        super().__init__(parent=parent)
        self.parent = parent
        self.ui = ui
        self.collapsed = initial_collapsed
        self._animation = None

        self.ui.btn_toggle_menu.clicked.connect(self.toggle)

    def set_collapsed(self, collapsed: bool):
        if collapsed != self.collapsed:
            self.toggle()

    collapsed_changed = Signal(bool)

    def _create_new_animation(self):
        new_animation = QPropertyAnimation(self.ui.menu_middle_frame, b"minimumWidth")
        new_animation.setDuration(150)
        new_animation.setStartValue(self.ui.menu_bar.width())
        new_width = 160 if self.collapsed else 30
        new_animation.setEndValue(new_width)
        return new_animation

    def toggle(self):
        self._animation = self._create_new_animation()
        # self._animation.finished.connect(self._toggle)
        # `finished` would be proper, however, this is never emitted so we use `stateChanged`
        self._animation.stateChanged.connect(self._toggle)
        self._animation.start()

    def _toggle(self):
        if self.collapsed:
            self.ui.btn_load_data.setText("Load data")
            self.ui.btn_export.setText("Export data")
            self.ui.btn_use_algorithm.setText("Use algorithm")
            self.ui.btn_load_data_gui_format.setText("Reload displayed data")
            self.ui.btn_save_data_gui_format.setText("Save displayed data")
            self.collapsed = False
        else:
            self.ui.btn_load_data_gui_format.setText("")
            self.ui.btn_use_algorithm.setText("")
            self.ui.btn_load_data.setText("")
            self.ui.btn_save_data_gui_format.setText("")
            self.ui.btn_export.setText("")
            self.collapsed = True
        self.collapsed_changed.emit(self.collapsed)
        self._animation.stateChanged.disconnect(self._toggle)
