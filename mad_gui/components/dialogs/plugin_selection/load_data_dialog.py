"""A dialog which is used internally by the GUI to select data/video/annotation files and an importer."""

import traceback
import warnings
from pathlib import Path

import pandas as pd
from PySide2 import QtCore
from PySide2.QtGui import Qt
from PySide2.QtUiTools import loadUiType
from PySide2.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton

from mad_gui import BaseFileImporter
from mad_gui.components.dialogs.user_information import UserInformation
from mad_gui.components.helper import ask_for_file_name, set_cursor
from mad_gui.config import Config
from mad_gui.qt_designer import UI_PATH
from mad_gui.utils.helper import resource_path
from mad_gui.utils.model_base import BaseStateModel, Property
from typing import Any, Dict, List, Optional, Tuple, Type

LINK_IMPLEMENT_IMPORTER = "https://mad-gui.readthedocs.io/en/latest/customization.html#implement-an-importer"

ui_path = resource_path(str(UI_PATH / "load.ui"))
if ".ui" in ui_path:
    try:
        LoadWindow, _ = loadUiType(ui_path)
    except TypeError:
        try:
            import sys
            import os

            uic_path = Path(os.sep.join(sys.executable.split(os.sep)[:-1])) / "Scripts"
            sys.path.append(str(uic_path))
            LoadWindow, _ = loadUiType(ui_path)
        except TypeError as e:
            raise FileNotFoundError(
                "Probably python did not find `pyside2-uic`. See "
                '"https://mad-gui.readthedocs.io/en/latest/troubleshooting.html#pyside2-uic-not-found" for more '
                "information"
            ) from e


elif ".py" in ui_path:
    from mad_gui.qt_designer.build.load import Ui_Form as LoadWindow  # noqa


class FileLoaderDialogState(BaseStateModel):
    data_file = Property("", dtype=str)
    video_file = Property("", dtype=str)
    annotation_file = Property("", dtype=str)


class FileLoaderDialog(QDialog):
    """A dialog, opened upon pressing `Load data` button in the GUI - interface to use importers.

    When the user wants to load data, they use this dialog. In the dialog, the user can use a dropdown menu to select an
    importer they want to use. This importer must previously have been passed to the GUI via the
    :meth:`mad_gui.start_gui`. The importer can be created as described in :ref:`implement importer`.

    Parameters
    ----------
    base_dir
        A base directory, which should be shown when the use wants to select a file - you can configure this by
        passing a `data_dir` to :meth:`mad_gui.start_gui`.
    loaders
        All the importers that were passed to :meth:`mad_gui.start_gui`, which will be shown in the dropdown.
    parent
        It is used to set the window and button style
    initial_state
        Will be assigned to `self.state`, which keeps the data of this view.

    Methods
    -------
    get_data
        After instantiating this class, use this method to open the dialog. Then, the user selects importer and data
        and this returns the loaded data in the MaD GUI format,
        see :meth:`mad_gui.plugins.BaseFileImporter.load_sensor_data`.
    validate_data_format
        Check whether the importer returned data in the expected formats and throw messages on what went wrong, if so.
    """

    final_data_: Dict[str, Dict[str, Any]]
    loader_: BaseFileImporter

    def __init__(
        self,
        base_dir: Path,
        loaders: List[BaseFileImporter],
        parent=None,
        initial_state: Optional[FileLoaderDialogState] = None,
    ):
        super().__init__()
        self.loaders = loaders
        self.parent = parent
        self.base_dir = base_dir

        self.state = initial_state
        if self.state is None:
            self.state = FileLoaderDialogState()

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

        self.ui.btn_ok.clicked.connect(self._handle_ok_click)
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
        self.ui.combo_plugin.view().setStyleSheet(style_cb.replace("QComboBox", "QListView"))

    def _handle_file_select(self, property_name):
        loader = self.loaders[self.ui.combo_plugin.currentIndex()]
        try:
            file_type = loader.file_type[property_name]
        except KeyError:
            # apparently the plugin does not restrict files to be displayed in openfiledialog
            file_type = ""
        file_name = ask_for_file_name(self.base_dir, parent=self, file_type=file_type)
        if file_name is not None:
            self.state.set(property_name, file_name)
            self.base_dir = str(Path(file_name).parent)

    def _handle_ok_click(self):
        """Use the selected loader for the selcted data.

        Additionally, this changes to cursor to `busy` for user feedback while loading the data.
        """
        set_cursor(self, QtCore.Qt.BusyCursor)
        final_data, loader = self._process_data()
        set_cursor(self, QtCore.Qt.ArrowCursor)
        if final_data is None or loader is None:
            return
        self.final_data_ = final_data

        self.accept()

    def _process_data(self):
        if not self.state.data_file:
            UserInformation().inform("You need to select a sensor data file!")
            return None, None

        # Get loader from combobox
        self.loader_ = self.loaders[self.ui.combo_plugin.currentIndex()]
        try:
            # TODO: Implement loader config
            user_config = {}
            loader = self.loader_._configure(parent=self, **user_config)
        except Exception as e:  # noqa
            # ignore bare except because anything can go wrong in a user-implemented plugin
            print(e)
            UserInformation().inform(f"Error configuring the plugin {self.loader_.name}:\n\n {e}")
            return None, None

        try:
            data = loader.load_sensor_data(self.state.data_file)
        except Exception as e:  # noqa
            self.setCursor(Qt.ArrowCursor)
            UserInformation.inform(
                f"There was an error loading the data ({str(e)}). Maybe you selected a wrong file or a wrong "
                f"recording system in the dropdown box?"
                f"\n\n"
                f"For the complete error message, see the terminal.\n"
            )
            warnings.warn(traceback.format_exc())
            return None, None

        self.validate_data_format(data)

        if self.state.annotation_file:
            annotations = loader.load_annotations(self.state.annotation_file)
            data = self._incorporate_annotations_to_data(data, annotations)

        return_dict = {
            "plot_data_dicts": data,
            "data_file_name": self.state.data_file,
            "start_time": loader.get_start_time(self.state.data_file),
        }

        if self.state.video_file:
            # Note: this must be done after loading data, since loading video might trigger plotting yellow lines in
            # the plots for video-signal-synchronization
            return_dict = self._handle_video_file(return_dict, loader)

        return return_dict, loader

    def validate_data_format(self, plot_data: Dict):
        if not isinstance(plot_data, dict):
            UserInformation.inform(
                "The loader's `load_sensor_data` method must return a dict, where the keys are the names you would "
                "like to give the plots. "
                "Click `Learn More` for more information.",
                help_link=LINK_IMPLEMENT_IMPORTER,
            )
            raise KeyError(
                f"{self.loader_.name()}'s  `load_sensor_data` method must return a dict. See {LINK_IMPLEMENT_IMPORTER}"
            )

        for plot, data in plot_data.items():
            if "sensor_data" not in data.keys():
                UserInformation.inform(
                    "Missing key `sensor_data` in the nested dict returned by the loader. See console output for "
                    "more information or click the link below to see what the importer should return",
                    help_link=LINK_IMPLEMENT_IMPORTER,
                )
                raise KeyError(
                    f"{self.loader_.name()} returned data to be plotted with the name {plot}. {plot} does not contain a"
                    f" key `sensor_data`, but is expected to. `sensor_data` in turn should keep a pd.DataFrame, "
                    f"where the columns are the channels to plot and each row is one sample to plot. "
                    f"See {LINK_IMPLEMENT_IMPORTER}"
                )

            if "sampling_rate_hz" not in data.keys():
                UserInformation.inform(
                    "Missing key `sampling_rate_hz` in the nested dict returned by the loader. See console output for "
                    "more information or click the link below to see what the importer should return",
                    help_link=LINK_IMPLEMENT_IMPORTER,
                )
                raise KeyError(
                    f"{self.loader_.name()} returned data to be plotted with the name {plot}. {plot} does not contain a"
                    f" key `sampling_rate_hz`, but is expected to. `sampling_rate_hz` in turn should keep a float. "
                    f"See {LINK_IMPLEMENT_IMPORTER}"
                )
            sensor_data = data.get("sensor_data", None)

            if not isinstance(sensor_data, pd.DataFrame):
                UserInformation.inform(
                    text="Data format was not valid. If you are a developer, see the command line for more detailed "
                    "information or click `Learn More` to get to our documentation about importers.",
                    help_link=LINK_IMPLEMENT_IMPORTER,
                )
                raise KeyError(
                    f"You tried to load data named {plot} using {self.loader_.name()}'s `load_sensor_data`. However, "
                    f"the key `sensor_data` keeps data of the type {type(sensor_data)}, although it should be a "
                    f"pandas DataFrame. See {LINK_IMPLEMENT_IMPORTER} for more info."
                )

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

    def get_data(self) -> Optional[Tuple[Dict[str, Dict[str, Any]], BaseFileImporter]]:
        """Run this dialog and return the data, that was selected by the user."""
        if self.exec_():
            return self.final_data_, self.loader_
        return None, None
