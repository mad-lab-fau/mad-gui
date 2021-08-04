"""This builds a GUI which can
a) load and show IMU data
b) apply an algorithm for stride segmentation and event detection
c) be used to manually add/delete/adapt labels for strides and/or activites.

isort:skip_file (Required import order: PySide2, pyqtgraph, mad_gui.*)
"""

import os
import warnings
from pathlib import Path
import pickle
from typing import Dict, List

import pandas as pd
import pyqtgraph as pg
from PySide2.QtCore import Qt
from PySide2.QtUiTools import loadUiType
from PySide2.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
    QMainWindow,
)

from mad_gui.components.dialogs.data_selector import DataSelector
from mad_gui.components.dialogs.export_results_dialog import ExportResultsDialog
from mad_gui.components.dialogs.load_data_dialog import LoadDataDialog
from mad_gui.components.dialogs.user_information import UserInformation
from mad_gui.components.helper import set_cursor
from mad_gui.components.key_event_handler import KeyEventHandler
from mad_gui.components.sidebar import Sidebar
from mad_gui.config import Config, BaseSettings, BaseTheme
from mad_gui.models.global_data import GlobalData, PlotData
from mad_gui.models.ui_state import UiState, PlotState, MODES
from mad_gui.plot_tools import SensorPlot, BaseRegionLabel
from mad_gui.plot_tools.video_plot import VideoPlot
from mad_gui.plugins.base import BaseExporter, BaseImporter
from mad_gui.plugins.helper import filter_plugins
from mad_gui.state_keeper import StateKeeper
from mad_gui.utils.helper import resource_path
from mad_gui.windows import VideoWindow
from mad_gui.qt_designer import UI_PATH

pg.setConfigOption("useOpenGL", False)

# CI can't handle openGL
if os.environ.get("GITHUB_CI"):
    # helps to make plot zooming smooth even when line width >1
    pg.setConfigOption("useOpenGL", False)

# Make sure that graphs are properly scaled when having multiple screens
# QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
# .setAttribute(Qt.AA_EnableHighDpiScaling)

ui_path = resource_path(str(UI_PATH / "main.ui"))
if ".ui" in ui_path:
    Window, _ = loadUiType(ui_path)
elif ".py" in ui_path:
    from mad_gui.qt_designer.build.main import Ui_MainWindow as Window  # pylint: disable=import-error


class MainWindow(QMainWindow):
    """This class implements the functionalities of the buttons in the GUI.
    Furthermore, it serves as an interface to Input-Output files, which are different for each data source,
    see our `General Information` part of the docs, section `Adding support for other systems`."""

    def __init__(self, parent=None, data_dir=None, settings=BaseSettings, theme=BaseTheme, plugins=None, labels=None):
        super().__init__()

        if plugins is None:
            plugins = []

        Config.set_theme(theme)
        Config.set_settings(settings)
        self.global_data = GlobalData(parent=self)
        self.ui_state = UiState(parent=self)
        self.plot_state = PlotState(parent=self)
        self.global_data.labels = labels

        self.parent = parent

        # Setting up the UI
        self.ui = Window()
        self.ui.setupUi(self)
        self._set_window_properties()

        # Register sidebar component logic
        self.menu = Sidebar(self.ui, parent=parent)
        self.ui_state.bind_bidirectional(self.menu.set_collapsed, self.menu.collapsed_changed, "menu_collapsed")
        self.menu.set_collapsed(False)

        # Setting up additional windows
        self.VideoWindow = VideoWindow(parent=self)
        self.data_selector = None

        # can only be done after adding the windows above
        self.label_buttons = {
            "add": self.ui.btn_add_label,
            "edit": self.ui.btn_edit_label,
            "remove": self.ui.btn_remove_label,
            "sync": self.ui.btn_sync_data,
        }

        # Setting up the plots
        self.sensor_plots = {}
        self.video_plot = None

        self._configure_buttons()

        # Setting up some attributes
        self.data_types = None  # data that the user wants to load/save (sensor, activities, and/or strides)
        self._user_is_informed = False

        self.closeEvent = self._close_event  # doing this to have consistent method naming

        self.global_data.bind(self.ui.label_displayed_data.setText, "data_file")
        self.global_data.bind(self._plot_data, "plot_data", initial_set=False)
        self.global_data.bind(self._set_sync, "sync_file", initial_set=False)
        self.plot_state.bind(self._update_button_state, "mode", initial_set=True)

        # Setup Key Event handler
        self.key_event_handler = KeyEventHandler(plot_state=self.plot_state, parent=self)
        self.keyPressEvent = self.key_event_handler.key_pressed

        StateKeeper.setParent(self)
        StateKeeper.announce_data_types.connect(self._set_data_types)
        StateKeeper.save_sync.connect(self._save_sync)

        # Note: Need to make all connections and ui setup before updating the value
        self.global_data.base_dir = data_dir
        self.global_data.plugins = list(plugins)

    def _enable_buttons(self, enable: bool):
        """In the beginning we want the user to load data, so we just show the two buttons."""
        for button in [
            self.ui.btn_add_label,
            self.ui.btn_edit_label,
            self.ui.btn_remove_label,
            self.ui.btn_sync_data,
            self.ui.btn_export,
            self.ui.btn_save_data_gui_format,
            self.ui.btn_use_algorithm,
        ]:
            if len(self.sensor_plots) == 1 and button == self.ui.btn_sync_data:
                continue
            button.setDisabled(not enable)

    def is_data_plotted(self):
        return bool(self.sensor_plots)

    def _configure_buttons(self):
        # buttons menu
        self.ui.btn_use_algorithm.clicked.connect(self.use_algorithm)
        self.ui.btn_load_data.clicked.connect(self.import_data)
        self.ui.btn_save_data_gui_format.clicked.connect(self.save_data_gui_format)
        self.ui.btn_export.clicked.connect(self.export)
        self.ui.btn_load_data_gui_format.clicked.connect(self._handle_load_data_gui_format)
        # buttons manual annotation
        for k, b in self.label_buttons.items():
            b.setObjectName(k)
            b.toggled.connect(self.on_main_buttons_clicked)
        self._enable_buttons(False)

    def on_main_buttons_clicked(self, new_state):
        button = self.sender()
        if new_state is False:
            self.plot_state.mode = "investigate"
            return
        self.plot_state.mode = button.objectName()

    def _update_button_state(self, new_mode: MODES):
        for k, b in self.label_buttons.items():
            old_state = b.blockSignals(True)
            b.setChecked(k == new_mode)
            b.blockSignals(old_state)

    def _unlink_plots(self):
        for plot in [*self.sensor_plots, self.ui.video_plot]:
            plot.set_coupled_plot(None)

    def _save_sync(self):
        sync = pd.DataFrame()
        main_plot = self._get_main_plot()
        if hasattr(Config.settings, "SENSORS_SYNCHRONIZED") and Config.settings.SENSORS_SYNCHRONIZED:
            for plot in self.sensor_plots.values():
                if plot == main_plot:
                    continue
                plot.sync_info = main_plot.sync_info
        self._link_plots()

        for plot_name, plot in self.sensor_plots.items():
            sync = pd.concat([sync, pd.DataFrame(data=plot.sync_info, columns=[plot_name])], axis=1)
        sync = pd.concat([sync, pd.DataFrame(data=self.video_plot.sync_info, columns=["Video"])], axis=1)
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Synchronization File", filter="*.xlsx")
        if file_name is None:
            return
        sync.to_excel(file_name)
        for plot in self.sensor_plots.values():
            plot.adapt_to_opening_video_window()

    def _handle_load_data_gui_format(self):
        if self.is_data_plotted():
            answer = UserInformation().confirm("Plotted data might be overwritten. Do you want to continue?")
        else:
            answer = QMessageBox.Yes

        if answer == QMessageBox.Yes:
            file = self._ask_for_file_name()
            self.load_data_from_pickle(file)

    def _ask_for_file_name(self):
        data_file = QFileDialog().getOpenFileName(None, "Select file to open", str(self.global_data.base_dir))[0]
        if data_file == "":
            # User clicked cancel
            return None
        self.global_data.data_file = data_file
        return data_file

    def _set_data_types(self, types: Dict):
        """Saves which of [sensor data, activity labels, stride labels] the user wants to load/save."""
        self.data_types = types

    def load_data_from_pickle(self, file: str):
        """Load data from a .mad_gui file.

        Parameters
        ----------
        file
            Full path to to a file that ends with `.mad_gui`. This file was previously created using
            :func:`~mad_gui.MainWindow.save_data_gui_format` and contains sensor data, activity labels and stride
            labels.
            However, the user might previously have selected that not all of those should be loaded.
            Which parts should be loaded is stored in `self.data_types`.
        """
        if file.split(".")[-1] != "mad_gui":
            UserInformation.inform("Can only load files that end with '.mad_gui'.")
            return None, None
        self.setCursor(Qt.BusyCursor)
        loaded_data = pd.read_pickle(file)

        if isinstance(loaded_data, GlobalData):
            print("new method.")

        label_classes_to_load = []
        for sensor_item in loaded_data.values():
            sensor_item = self._make_keys_backwards_compatible(sensor_item)
            # we assume that everything that has not the following words in it are labels
            labels = [key for key in sensor_item.keys() if key not in ["sensor", "data", "sampling_rate_hz"]]
            label_classes_to_load.extend(labels)

        processable_label_classes = self._get_processable_label_classes(label_classes_to_load)
        unknown_label_classes = []
        for label_class in label_classes_to_load:
            if not any([label.__name__ == label_class for label in processable_label_classes]):
                unknown_label_classes.append(label_class)

        if len(unknown_label_classes) > 0:
            UserInformation.inform(
                f"The saved data has labels which this GUI does not know.\n\n"
                f"Unknown label class: {unknown_label_classes}\n"
            )
            warnings.warn("Implement link to help.")
        loadable_labels = [label for label in processable_label_classes if label.__name__ in label_classes_to_load]

        # Doing it in two lines, and exposing via self to enable testing this whole method
        self.data_selector = DataSelector(parent=self, labels=set(loadable_labels))
        self.data_selector.ask_user()

        if not self.data_types["sensor"] and not self.global_data.plot_data:
            UserInformation.inform(
                "Can only plot labels if data is plotted. Please also tick 'Sensor data' or "
                "load sensor data using the 'Load Data' button on the upper left."
            )
            self.setCursor(Qt.ArrowCursor)
            return None, None

        selected_data = [data_type for data_type, use in self.data_types.items() if use]

        plot_data = {}
        for plot_name, data in loaded_data.items():
            plot_data[plot_name] = PlotData().from_dict(data, selections=selected_data)

        self.global_data.plot_data = plot_data
        self.global_data.base_dir = Path(file).parent

        self.setCursor(Qt.ArrowCursor)
        self._enable_buttons(True)
        self.menu.set_collapsed(True)

        return loaded_data, processable_label_classes

    @staticmethod
    def _make_keys_backwards_compatible(sensor_item: Dict):
        for t in [("stride_annotations", "StrideLabel"), ("activity_annotations", "ActivityLabel")]:
            try:
                sensor_item[t[1]] = sensor_item.pop(t[0])
            except KeyError:
                pass
        return sensor_item

    def _get_processable_label_classes(self, labels: List):
        known_label_types = {label.__name__: label for label in self.global_data.labels}
        known_label_types = self._label_classes_backwards_compatibility(labels, known_label_types)
        return [v for k, v in known_label_types.items()]

    def _label_classes_backwards_compatibility(self, labels, known_label_types: Dict):
        class StrideLabel(BaseRegionLabel):
            name = "Stride Label"
            min_height = 0.25
            max_height = 0.75

        class ActivityLabel(BaseRegionLabel):
            name = "Activity Label"
            min_height = 0.75
            max_height = 1

        for label_class in [StrideLabel, ActivityLabel]:
            if label_class.__name__ in labels:
                known_label_types[label_class.__name__] = label_class
                if label_class.__name__ not in [label.__name__ for label in self.global_data.labels]:
                    self.global_data.labels = (*self.global_data.labels, label_class)
        return known_label_types

    def import_data(self):
        """Start dialog to import data.

        This will open a :class:`mad_gui.LoadDataWindow`. In there, the user can select data to be loaded:

            - sensor data
            - annotations
            - video

        Additionally, the user can select the system that was used to record the sensor data and annotations.
        Depending on this selection, the path of the data to be loaded will be passed to the regarding importer in
        :mod:`mad_gui.plugins`.

        """
        # TODO: Add dialog warning if data is already plotted
        view = LoadDataDialog(
            self.global_data.base_dir, loaders=filter_plugins(self.global_data.plugins, BaseImporter), parent=self
        )
        data, loader = view.get_data()
        if data is None or loader is None:
            return
        self.global_data.active_loader = loader
        self.global_data.data_file = data.get("data_file_name", "")
        self.global_data.sync_file = data.get("sync_file", "")
        self.global_data.video_file = data.get("video_file", "")
        plot_data = {
            k: PlotData().from_dict(v, selections=["sensor", *[item.__name__ for item in self.global_data.labels]])
            for k, v in data.get("data", {}).items()
        }
        self.global_data.plot_data = plot_data
        self.load_video(data.get("video_file", None))
        self._set_sync(data.get("sync_file", None))
        self._enable_buttons(True)
        self.menu.set_collapsed(True)

    def _set_sync(self, sync_file: str):
        """Set the synchronization for each plot"""
        if not sync_file:
            return
        sync = self.global_data.active_loader.get_video_signal_synchronization(sync_file)
        unsynced_sensors = []
        for plot_name, plot in self.sensor_plots.items():
            try:
                plot.sync_info = sync[plot_name]
                plot.adapt_to_opening_video_window()
            except KeyError:
                unsynced_sensors.append(plot_name)
        if len(unsynced_sensors) > 1:
            UserInformation.inform(
                f"Found a synchronization file ({sync_file}), however there is no info about "
                f"the sensor(s) {unsynced_sensors}, therefore it is not synchronized."
            )
        if self.video_plot:
            self.video_plot.sync_info = sync["Video"]

    def _plot_data(self, data_dict: Dict[str, PlotData]):
        # if len(StateKeeper.loaded_data) == 3:
        #     start_time = StateKeeper.loaded_data[2]
        # else:
        # TODO: Implement start time
        start_time = None
        set_cursor(self, Qt.BusyCursor)

        # Delete all existing plots
        plot_wrapper: QVBoxLayout = self.ui.plotwidget
        for i_plot in list(self.sensor_plots.values()):
            plot_wrapper.removeWidget(i_plot)
            i_plot.deleteLater()
            del i_plot
        self.sensor_plots = {}

        # Create new plots
        for sensor_name, data in data_dict.items():
            plot = SensorPlot(
                plot_data=data,
                initial_plot_channels=Config.settings.CHANNELS_TO_PLOT,
                start_time=start_time,
                label_classes=self.global_data.labels,
                parent=self,
            )
            plot_wrapper.addWidget(plot)
            self.sensor_plots[sensor_name] = plot
            plot.set_title(sensor_name)
            # Bind global mode change
            self.plot_state.bind_property_bidirectional(plot.state, "mode", "mode", initial="set")

        plots = list(self.sensor_plots.values())
        plots[0].is_main_plot = True

        # Bind the ranges of all plots together, if settings say Consts.settings says so
        self._link_plots()
        # TODO: if self.plot_state.mode changes from sync to something else, we want to bind the plots again
        set_cursor(self, Qt.ArrowCursor)

    def _link_plots(self):
        for p in self.sensor_plots.values():
            if p.is_main_plot:
                continue
            self._get_main_plot().set_coupled_plot(p)

    def load_video(self, video_path):
        if not video_path:
            return
        self.VideoWindow.start_video(video_path)
        self.VideoWindow.show()
        StateKeeper.video_duration_available.connect(self._initialize_video_plot)
        self.ui.btn_sync_data.setDisabled(False)

    def _initialize_video_plot(self):
        StateKeeper.video_duration_available.disconnect(self._initialize_video_plot)
        if self.video_plot:
            self.ui.plotwidget.removeWidget(self.video_plot)
        self.video_plot = VideoPlot(parent=self, video_window=self.VideoWindow)
        self.video_plot.set_title("Video Plot")
        self.video_plot.hide()
        self.ui.plotwidget.addWidget(self.video_plot)
        self.plot_state.bind_property_bidirectional(self.video_plot.state, "mode", "mode", initial="set")

    def _get_main_plot(self):
        return [plot for plot in self.sensor_plots.values() if plot.is_main_plot][0]

    def use_algorithm(self):
        """Applies an algorithm to the plotted IMU data.

        This will basically call :func:`mad_gui.plugins.BaseImporter.annotation_from_data`. Instead of the
        `BaseImporter` a different importer specified in the :class:`mad_gui.LoadDataWindow` (dropdown menu)
        might be used.

        The activity and/or stride labels that will be generated by that method will then be passed to the plots,
        which will subsequently plot the labels, see :func:`mad_gui.plot_tools.SensorPlot.set_activity_labels` and
        :func:`mad_gui.plot_tools.SensorPlot._set_stride_labels`.

        """
        if not self.is_data_plotted() or self.global_data.active_loader is None:
            UserInformation(parent=self).inform("Please load sensor data before continuing.")
            return

        if not UserInformation(parent=self).confirm(
            "Warning: Calculating new annotations might delete all currently "
            "displayed annotations!\nIt is up to the implemented algorithm, "
            "if the new annotations are added or if they replace the old "
            "annotations."
        ):
            return

        # Set state to investigate to force updating global state from plot
        self.plot_state.mode = "investigate"

        set_cursor(self, Qt.BusyCursor)
        try:
            for plot_data in self.global_data.plot_data.values():
                annotations = self.global_data.active_loader.annotation_from_data(plot_data=plot_data)
                if "strides" in annotations:
                    plot_data.stride_annotations = annotations["strides"]
                if "activities" in annotations:
                    plot_data.activity_annotations = annotations["activities"]
        except (AttributeError, NotImplementedError):
            set_cursor(self, Qt.ArrowCursor)
            return

        set_cursor(self, Qt.ArrowCursor)

    def _save_data(self, data_to_save: PlotData):
        save_file_name = QFileDialog().getSaveFileName(
            None, "Save GUI data", str(Path(self.global_data.data_file).parent) + "/data.mad_gui", "*.mad_gui"
        )[0]
        if save_file_name != "":
            pickable_data = {k: v.to_dict() for k, v in data_to_save.items()}
            with open(save_file_name, "wb") as file:
                pickle.dump(pickable_data, file, protocol=pickle.HIGHEST_PROTOCOL)

    def save_data_gui_format(self):
        """Saves the displayed sensor data, sampling rate and displayed activity and stride labels into a pickle file.

        The file ending will be `.mad_gui` to make clear it can be loaded again by this GUI. The data can be
        re-loaded into the GUI using the `Load Data GUI format` button.
        If you want to load this data in an other application / script you can so by using :func:`pandas.read_pickle()`.
        """
        if not self.is_data_plotted():
            UserInformation.inform("Please load data before continuing.")
            return

        # Set state to investigate to force updating global state from plot
        self.plot_state.mode = "investigate"

        self._save_data(self.global_data.plot_data)
        StateKeeper.set_has_unsaved_changes(False)

    def export(self):
        """Called when clicking the `Export data` button.

        This button should be used to calculate features from the annotations. For example to calculate a
        mean length of certain activities or strides. To do so, it a :class:`mad_gui.ExportResultsWindow`,
        which basically just is used to select one of the exporters in :mod:`mad_gui.plugins`."""

        if not self.is_data_plotted():
            UserInformation(parent=self).inform("Please to load data before continuing.")
            return

        # Set state to investigate to force updating global state from plot
        self.plot_state.mode = "investigate"

        ExportResultsDialog(exporters=filter_plugins(self.global_data.plugins, BaseExporter), parent=self).export_data(
            self.global_data
        )

    def _close_event(self, ev):
        if StateKeeper.gui_has_unsaved_changes:
            answer = UserInformation().confirm("Recent changes have not been saved. Are you sure you want to exit?")
            if answer == QMessageBox.No:
                ev.ignore()
                return
        if self.VideoWindow:
            self.VideoWindow.close()
        self.close()

    def _set_window_properties(self):
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("MaD GUI")
