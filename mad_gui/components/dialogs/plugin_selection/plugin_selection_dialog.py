from typing import List, Union

from PySide6 import QtCore
from PySide6.QtWidgets import QDialog

from mad_gui.components.dialogs.user_information import UserInformation
from mad_gui.components.helper import set_cursor
from mad_gui.models.global_data import GlobalData
from mad_gui.models.local import PlotData
from mad_gui.plugins.base import BaseAlgorithm, BaseExporter
from mad_gui.qt_designer import UI_PATH
from mad_gui.utils.helper import load_window_from_file

UiForm = load_window_from_file(UI_PATH / "plugin_selection.ui", "plugin_selection")


class PluginSelectionDialog(QDialog):
    """A dialog to select the plugin to use.

    See Also
    --------
    :class:`~mad_gui.windows.BasePluginSelector`

    """

    _data: PlotData

    def __init__(self, plugins: List[Union[BaseAlgorithm, BaseExporter]], parent=None):
        super().__init__()
        self.plugins = plugins
        self.parent = parent
        self.ui = UiForm()
        self.setWindowIcon(parent.windowIcon())
        self.ui.setupUi(self)
        self.setStyleSheet(parent.styleSheet())
        self._setup_ui()
        self.executed_plugin = None

    def _setup_ui(self):
        self.setWindowTitle("Select Plugin")
        self.ui.combo_plugin.addItems([plugin.get_name() for plugin in self.plugins])
        self.ui.btn_ok.clicked.connect(self._start_processing)
        self.ui.btn_cancel.clicked.connect(self.close)

        for btn in [
            self.ui.btn_ok,
            self.ui.btn_cancel,
        ]:
            btn.setStyleSheet(self.parent.ui.btn_add_label.styleSheet())

        style_cb = self.parent.ui.btn_add_label.styleSheet().replace("QPushButton", "QComboBox")
        self.ui.combo_plugin.setStyleSheet(style_cb)
        self.ui.combo_plugin.view().setStyleSheet(style_cb.replace("QComboBox", "QListView"))

    def _start_processing(self):
        set_cursor(self, QtCore.Qt.BusyCursor)
        out = self._process_data()
        set_cursor(self, QtCore.Qt.ArrowCursor)
        if not out:
            return
        self.accept()

    def _process_data(self):
        """Use the selected plugin to create a dataframe to be exported into an excel file.

        The emitted signal will be fetched by :class:`mad_gui.windows.MainWindow`, which will in turn trigger the
        loading by the regarding importer. Also, the mode of the GUI will be set to `investigate`.
        """
        try:
            plugin = self.plugins[self.ui.combo_plugin.currentIndex()]
        except IndexError:
            UserInformation.inform("No methods for exporting are implemented.")
            return False
        try:
            # TODO: Implement loader config
            user_config = {}
            plugin = plugin._configure(parent=self, **user_config)
        except Exception as error:  # pylint: disable=broad-except
            # broad exception on purpose because we do not know which exceptions might be thrown by an plugin
            # created by someone else
            UserInformation().inform(f"Error configuring Plugin {plugin.get_name()} \n Error:\n {str(error)}")
            return False

        try:
            plugin.process_data(self._data)
            self.executed_plugin = plugin
        except Exception as error:
            UserInformation().inform(
                f"An error occured inside your plugin {plugin.get_name()}: {str(error)}\n"
                f"Try to debug by setting a breakpoint in your plugin {plugin.get_name()} or see the command line "
                f"for more information."
            )
            raise error
        return True

    def process_data(self, data: GlobalData):
        self._data = data
        self.exec_()
