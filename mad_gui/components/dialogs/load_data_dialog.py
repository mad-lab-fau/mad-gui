from pathlib import Path

from PySide2 import QtCore
from PySide2.QtUiTools import loadUiType
from PySide2.QtWidgets import QDialog

from mad_gui import BaseImporter
from mad_gui.components.dialogs.user_information import UserInformation
from mad_gui.components.helper import ask_for_file_name, set_cursor
from mad_gui.qt_designer import UI_PATH
from mad_gui.utils.helper import resource_path
from mad_gui.utils.model_base import BaseStateModel, Property
from typing import Any, Dict, List, Optional, Tuple, Type

ui_path = resource_path(str(UI_PATH / "load.ui"))
if ".ui" in ui_path:
    LoadWindow, _ = loadUiType(ui_path)
elif ".py" in ui_path:
    from mad_gui.qt_designer.build.load import Ui_Form as LoadWindow  # pylint: disable=C0412,E0401


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
        self._setup_ui()

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

    def _handle_file_select(self, property_name):
        file_name = ask_for_file_name(self.base_dir, parent=self)
        if file_name is not None:
            self.state.set(property_name, file_name)

    def process_data(self):
        set_cursor(self, QtCore.Qt.BusyCursor)
        out = self._process_data()
        set_cursor(self, QtCore.Qt.ArrowCursor)
        if out is None:
            return
        final_data, loader = out
        self.final_data_ = final_data
        self.loader_ = loader
        self.accept()

    def _process_data(self):
        # Get loader from combobox
        loader_class = self.loaders[self.ui.combo_plugin.currentIndex()]
        try:
            # TODO: Implement loader config
            user_config = {}
            loader = loader_class(parent=self, **user_config)
        except:  # noqa
            # ignore bare except because anything can go wrong in a user-implemented plugin
            UserInformation().inform("Error loading Plugin {}".format(loader_class.name()))
            return None, None

        if not self.state.data_file:
            UserInformation().inform("You need to select a sensor data file!")
            return None, None

        data, sampling_rate_hz = loader.load_sensor_data(self.state.data_file)
        annotations = {}
        if self.state.annotation_file:
            annotations = loader.load_annotations(self.state.annotation_file)

            if not set(annotations.keys()) == set(data.keys()):
                raise ValueError("The dict keys of the annotations must match the dict keys of the sensor data.")

        final_data = {}
        for sensor, sensor_data in data.items():
            final_data[sensor] = self._transform_annotations(sensor_data, sensor, sampling_rate_hz, annotations)

        return_dict = {"data": final_data, "data_file_name": self.state.data_file}

        if self.state.video_file:
            # Note: this must be done after loading data, since loading video might trigger plotting yellow lines in
            # the plots for video-signal-synchronization
            return_dict = self._handle_video_file(return_dict, loader)

        return return_dict, loader

    def _handle_video_file(self, return_dict, loader):
        return_dict["video_file"] = self.state.video_file
        sync_file = loader.get_sync_file(self.state.video_file)
        if sync_file:
            return_dict["sync_file"] = sync_file
        return return_dict

    @classmethod
    def _transform_annotations(cls, sensor_data, sensor, sampling_rate_hz, annotations):
        tmp = {"data": sensor_data, "sampling_rate_hz": sampling_rate_hz}
        if annotations:
            a = annotations[sensor]
            if "strides" in a:
                tmp["stride_annotations"] = a["strides"]
            if "activities" in a:
                tmp["activity_annotations"] = a["activities"]
            if set(a.keys()) - {"strides", "activities"}:
                raise ValueError(
                    "Loader provided annotations that were not understood. Only `strides` and `activities` are "
                    "supported as dict keys."
                )
        return tmp

    def get_data(self) -> Optional[Tuple[Dict[str, Dict[str, Any]], BaseImporter]]:
        if self.exec_():
            return self.final_data_, self.loader_
        return None, None
