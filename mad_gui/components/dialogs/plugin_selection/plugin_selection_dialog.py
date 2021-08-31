from mad_gui.components.dialogs.user_information import UserInformation
from mad_gui.components.helper import set_cursor
from mad_gui.config import Config
from mad_gui.models.global_data import GlobalData, PlotData
from mad_gui.plugins.base import BasePlugin
from mad_gui.qt_designer import UI_PATH
from mad_gui.utils.helper import resource_path
from PySide2 import QtCore
from PySide2.QtUiTools import loadUiType
from PySide2.QtWidgets import QDialog

from typing import List, Type

ui_path = resource_path(str(UI_PATH / "plugin_selection.ui"))
if ".ui" in ui_path:
    PluginSelectorWindow, _ = loadUiType(ui_path)
elif ".py" in ui_path:
    from mad_gui.qt_designer.build.export import Ui_Form as PluginSelectorWindow  # pylint: disable=C0412,E0401


class PluginSelectionDialog(QDialog):
    """A dialog to select the plugin to use to export results from the shown data and labels.

    See Also
    --------
    :class:`~mad_gui.windows.BasePluginSelector`

    """

    _data: PlotData

    def __init__(self, plugins: List[Type[BasePlugin]], parent=None):
        super().__init__()
        self.plugins = plugins
        self.parent = parent
        self.ui = PluginSelectorWindow()
        self.setWindowIcon(parent.windowIcon())
        self.ui.setupUi(self)
        self.setStyleSheet(parent.styleSheet())
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Select Plugin")
        self.ui.combo_plugin.addItems([plugin.name() for plugin in self.plugins])
        self.ui.btn_ok.clicked.connect(self._start_processing)
        self.ui.btn_cancel.clicked.connect(self.close)

        for btn in [
            self.ui.btn_ok,
            self.ui.btn_cancel,
        ]:
            btn.setStyleSheet(self.parent.ui.btn_add_label.styleSheet())

        light = Config.theme.COLOR_LIGHT
        style_cb = (
            f"QComboBox"
            f"{{\nborder:none;\npadding: 3px;\nbackground-color:rgb({light.red()}"
            f",{light.green()}"
            f",{light.blue()});\ntext-align: left;\n}}"
        )
        self.ui.combo_plugin.setStyleSheet(style_cb)

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
            plugin_class = self.plugins[self.ui.combo_plugin.currentIndex()]
        except IndexError:
            UserInformation.inform("No methods for exporting are implemented.")
            return False
        try:
            # TODO: Implement loader config
            user_config = {}
            plugin = plugin_class(parent=self, **user_config)
        except Exception as e:  # pylint: disable=broad-except
            # broad exception on purpose because we do not know which exceptions might be thrown by an plugin
            # created by someone else
            UserInformation().inform("Error loading Plugin {}".format(plugin_class.name()))
            print(e)
            return False

        try:
            plugin.process_data(self._data)
        except Exception as e:  # pylint: disable=broad-except
            # broad exception on purpose because we do not know which exceptions might be thrown by an plugin
            # created by someone else
            UserInformation().inform(f"An error occured: {e}")
            return False

        return True

    def process_data(self, data: GlobalData):
        self._data = data
        self.exec_()
