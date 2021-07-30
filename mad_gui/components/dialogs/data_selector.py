"""Select which kind of data should be loaded/saved."""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QVBoxLayout

from mad_gui.state_keeper import StateKeeper


class DataSelector(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowModality(Qt.ApplicationModal)
        self.setPalette(self.parent.palette())
        self.vbox = QVBoxLayout()
        self.add_checkboxes_to_vbox()
        self.add_ok_btn()
        self.setLayout(self.vbox)
        self.setWindowTitle("Select data types")

    def add_checkboxes_to_vbox(self):
        self.box_data = QCheckBox("Sensor data")
        self.box_data.setCheckState(Qt.Checked)
        self.box_activities = QCheckBox("Activity labels")
        self.box_data.setCheckState(Qt.Checked)
        self.box_strides = QCheckBox("Stride labels")
        self.box_strides.setCheckState(Qt.Checked)
        self.vbox.addWidget(self.box_data)
        self.vbox.addWidget(self.box_activities)
        self.vbox.addWidget(self.box_strides)

    def add_ok_btn(self):
        ok_btn = QDialogButtonBox(QDialogButtonBox.Ok)
        button_style = self.parent.ui.btn_add_label.styleSheet()
        ok_btn.setStyleSheet(button_style)
        ok_btn.clicked.connect(self.handle_ok_click)
        self.vbox.addWidget(ok_btn)

    def handle_ok_click(self):
        data_to_load = {
            "sensor": self.box_data.isChecked(),
            "activities": self.box_activities.isChecked(),
            "strides": self.box_strides.isChecked(),
        }
        StateKeeper.announce_data_types.emit(data_to_load)
        self.close()

    def ask_user(self):
        self.exec_()
