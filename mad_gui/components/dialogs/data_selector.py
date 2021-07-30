"""Select which kind of data should be loaded/saved."""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QVBoxLayout

from mad_gui.state_keeper import StateKeeper


class DataSelector(QDialog):
    def __init__(self, parent=None, labels=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowModality(Qt.ApplicationModal)
        self.setPalette(self.parent.palette())
        self.vbox = QVBoxLayout()
        self.labels = labels
        self.add_checkboxes_to_vbox()
        self.add_ok_btn()
        self.setLayout(self.vbox)
        self.setWindowTitle("Select data types")

    def add_checkboxes_to_vbox(self):
        self.boxes = dict()
        self.boxes["sensor"] = QCheckBox("Sensor data")
        self.boxes["sensor"].setCheckState(Qt.Checked)
        self.vbox.addWidget(self.boxes["sensor"])
        for label in self.labels:
            self.boxes[label.__name__] = QCheckBox(label.name)
            self.boxes[label.__name__].setCheckState(Qt.Checked)
            self.vbox.addWidget(self.boxes[label.__name__])

    def add_ok_btn(self):
        self.ok_btn = QDialogButtonBox(QDialogButtonBox.Ok)
        button_style = self.parent.ui.btn_add_label.styleSheet()
        self.ok_btn.setStyleSheet(button_style)
        self.ok_btn.clicked.connect(self.handle_ok_click)
        self.vbox.addWidget(self.ok_btn)

    def handle_ok_click(self):
        data_to_load = {k: v.isChecked() for k, v in self.boxes.items()}
        #    "sensor": self.boxes["sensor"].isChecked(),
        #    "activities": self.box_activities.isChecked(),
        #    "strides": self.box_strides.isChecked(),
        # }
        StateKeeper.announce_data_types.emit(data_to_load)
        self.close()

    def ask_user(self):
        self.exec_()
