import warnings
from pathlib import Path

import pandas as pd
from PySide2 import QtCore
from PySide2.QtGui import Qt
from PySide2.QtUiTools import loadUiType
from PySide2.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton

from mad_gui import BaseImporter
from mad_gui.components.dialogs.user_information import UserInformation
from mad_gui.components.helper import ask_for_file_name, set_cursor
from mad_gui.config import Config
from mad_gui.qt_designer import UI_PATH
from mad_gui.utils.helper import resource_path
from mad_gui.utils.model_base import BaseStateModel, Property
from typing import Any, Dict, List, Optional, Tuple, Type

ui_path = resource_path(str(UI_PATH / "load.ui"))
if ".ui" in ui_path:
    try:
        LoadWindow, _ = loadUiType(ui_path)
    except TypeError as e:
        raise FileNotFoundError(
            "Probably python did not find `pyside2-uic`. See "
            '"https://mad-gui.readthedocs.io/en/latest/troubleshooting.html#pyside2-uic-not-found" for more information'
        ) from e


elif ".py" in ui_path:
    from mad_gui.qt_designer.build.load import Ui_Form as LoadWindow  # noqa


class LoadDataDialogState(BaseStateModel):
    data_file = Property("", dtype=str)
    video_file = Property("", dtype=str)
    annotation_file = Property("", dtype=str)


class LoadDataDialog(QDialog):
    final_data_: Dict[str, Dict[str, Any]]
    loader_: BaseImporter

    def __init__(
        self,
        base_dir: Path,
        loaders: List[Type[BaseImporter]],
        parent=None,
        initial_state: Optional[LoadDataDialogState] = None,
    ):
        super().__init__()
        self.loaders = loaders
        self.parent = parent
        self.base_dir = base_dir

        self.state = initial_state
        if self.state is None:
            self.state = LoadDataDialogState()

        self.ui = LoadWindow()
        self.setWindowIcon(parent.windowIcon())
        self.ui.setupUi(self)
        self.setStyleSheet(parent.styleSheet())
        self._setup_ui()
        self._init_position()

    def _init_position(self):
        """Move the window to the center of the parent window."""

        x = self.parent.pos().x() + self.parent.size().width() / 2 - self.size().width() / 2
        y = self.parent.pos().y() + self.parent.size().height() / 2 - self.size().height() / 2
        self.move(x, y)

    def _setup_ui(self):
        self.setWindowTitle("Load Data")
        self.ui.combo_plugin.addItems([loader.name() for loader in self.loaders])

        self.ui.btn_select_data.clicked.connect(lambda: self._handle_file_select("data_file"))
        self.ui.btn_select_video.clicked.connect(lambda: self._handle_file_select("video_file"))
        self.ui.btn_select_annotation.clicked.connect(lambda: self._handle_file_select("annotation_file"))

        self.state.bind_bidirectional(self.ui.qedit_data_path.setText, self.ui.qedit_data_path.textEdited, "data_file")
        self.state.bind_bidirectional(
            self.ui.qedit_video_path.setText, self.ui.qedit_video_path.textEdited, "video_file"
        )
        self.state.bind_bidirectional(
            self.ui.qedit_annotation_path.setText, self.ui.qedit_video_path.textEdited, "annotation_file"
        )

        self.ui.btn_ok.clicked.connect(self.process_data)
        self.ui.btn_cancel.clicked.connect(self.close)

        light = Config.theme.COLOR_LIGHT

        for label in self.findChildren(QLabel):
            label.setStyleSheet(f"color: rgb({light.red()},{light.green()},{light.blue()});")

        for edit in self.findChildren(QLineEdit):
            edit.setStyleSheet(f"color: rgb({light.red()},{light.green()},{light.blue()});")

        for elem in self.findChildren(QPushButton):
            elem.setStyleSheet(self.parent.ui.btn_add_label.styleSheet())

        style_cb = self.parent.ui.btn_add_label.styleSheet().replace("QPushButton", "QComboBox")
        self.ui.combo_plugin.setStyleSheet(style_cb)

    def _handle_file_select(self, property_name):
        file_name = ask_for_file_name(self.base_dir, parent=self)
        if file_name is not None:
            self.state.set(property_name, file_name)
            self.base_dir = str(Path(file_name).parent)

    def process_data(self):
        """Use the selected loader for the selcted data.

        Additionally, this changes to cursor to `busy` for user feedback while loading the data.
        """
        set_cursor(self, QtCore.Qt.BusyCursor)
        final_data, loader = self._process_data()
        set_cursor(self, QtCore.Qt.ArrowCursor)
        if final_data is None or loader is None:
            return
        self.final_data_ = final_data
        self.loader_ = loader
        self.accept()

    def _process_data(self):
        if not self.state.data_file:
            UserInformation().inform("You need to select a sensor data file!")
            return None, None

        # Get loader from combobox
        loader_class = self.loaders[self.ui.combo_plugin.currentIndex()]
        try:
            # TODO: Implement loader config
            user_config = {}
            loader = loader_class(parent=self, **user_config)
        except Exception as e:  # noqa
            # ignore bare except because anything can go wrong in a user-implemented plugin
            print(e)
            UserInformation().inform(f"Error creating an instance of the plugin {loader_class.name}:\n\n {e}")
            return None, None

        try:
            data = loader.load_sensor_data(self.state.data_file)
        except Exception as e:  # noqa
            self.setCursor(Qt.ArrowCursor)
            UserInformation.inform(
                "There was an error loading the data. Maybe you selected a wrong file or a wrong "
                "recording system in the dropdown box?"
                "\n\n"
                "Complete error message:\n"
                f"{str(e)}"
            )
            warnings.warn(str(e))
            return None, None

        self.validate_data_format(data)

        if self.state.annotation_file:
            annotations = loader.load_annotations(self.state.annotation_file)
            data = self._incorporate_annotations_to_data(data, annotations)

        return_dict = {"plot_data_dicts": data, "data_file_name": self.state.data_file}

        if self.state.video_file:
            # Note: this must be done after loading data, since loading video might trigger plotting yellow lines in
            # the plots for video-signal-synchronization
            return_dict = self._handle_video_file(return_dict, loader)

        return return_dict, loader

    def validate_data_format(self, data: Dict):
        if not isinstance(data, dict):
            UserInformation.inform(
                f"{self.loader_.name()}'s load_sensor_data method must return a dict. Click "
                f"`Learn More` for more information.",
                help_link="https://mad-gui.readthedocs.io/en/latest/customization.html#implement-an-importer",
            )
            warnings.warn(f"{self.loader_.name()}'s  `load_sensor_data` method must return a dict.")
        sensor_data = data.get(data, "sensor_data", None)

        if not isinstance(sensor_data, pd.DataFrame):
            UserInformation.inform(
                f"Please make sure, that the dict returned by {self.loader_.name()}'s "
                f"load_sensor_data method has a key `sensor_data`, which contains a pandas "
                f"DataFrame. Click `Learn More` for more information.",
                help_link="https://mad-gui.readthedocs.io/en/latest/customization.html#implement-an-importer",
            )
            warnings.warn("The importer's `load_sensor_data` method must return a dict.")

    @staticmethod
    def _incorporate_annotations_to_data(data: Dict, annotations: Dict) -> Dict:
        for sensor, annotation in annotations.items():
            try:
                data[sensor]["annotations"] = annotation
            except KeyError as k:
                UserInformation.inform(
                    "Loader provided annotations for sensors that have no plot. Click 'Learn More' "
                    "for more information",
                    help_link="https://mad-gui.readthedocs.io/en/latest/"
                    "troubleshooting.html#loader-provided-"
                    "annotations-that-were-not-understood",
                )

                raise ValueError(
                    "The dict keys of the annotations must match the dict keys of the sensor data. See "
                    "https://mad-gui.readthedocs.io/en/latest/troubleshooting.html#id2 for more "
                    "information."
                ) from k
        return data

    def _handle_video_file(self, return_dict, loader):
        return_dict["video_file"] = self.state.video_file
        sync_file = loader.get_sync_file(self.state.video_file)
        if sync_file:
            return_dict["sync_file"] = sync_file
        return return_dict

    def get_data(self) -> Optional[Tuple[Dict[str, Dict[str, Any]], BaseImporter]]:
        """Close this dialog and return the data, that was selected by the user."""
        if self.exec_():
            return self.final_data_, self.loader_
        return None, None
