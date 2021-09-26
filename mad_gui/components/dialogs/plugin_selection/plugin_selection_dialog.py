from PySide2 import QtCore
from PySide2.QtUiTools import loadUiType
from PySide2.QtWidgets import QDialog

from mad_gui.components.dialogs.user_information import UserInformation
from mad_gui.components.helper import set_cursor
from mad_gui.config import Config
from mad_gui.models.global_data import GlobalData
from mad_gui.models.local import PlotData
from mad_gui.plugins.base import BasePlugin
from mad_gui.qt_designer import UI_PATH
from mad_gui.utils.helper import resource_path
from typing import List, Type

ui_path = resource_path(str(UI_PATH / "plugin_selection.ui"))
if ".ui" in ui_path:
    try:
        UiForm, _ = loadUiType(ui_path)
    except TypeError as e:
        raise FileNotFoundError(
            "Probably python did not find `pyside2-uic`. See "
            '"https://mad-gui.readthedocs.io/en/latest/troubleshooting.html#pyside2-uic-not-found" for more information'
        ) from e

elif ".py" in ui_path:
    from mad_gui.qt_designer.build.plugin_selection import Ui_Form  # noqa


class PluginSelectionDialog(QDialog):
    """A dialog to select the plugin to use.

    See Also
    --------
    :class:`~mad_gui.windows.BasePluginSelector`

    """

    _data: PlotData

    def __init__(self, plugins: List[Type[BasePlugin]], parent=None):
        super().__init__()
        self.plugins = plugins
        self.parent = parent
        self.ui = UiForm()
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
        except Exception as error:  # pylint: disable=broad-except
            # broad exception on purpose because we do not know which exceptions might be thrown by an plugin
            # created by someone else
            UserInformation().inform(f"Error loading Plugin {plugin_class.name()}" f"\n Error:\n" f"{str(error)}")
            return False

        try:
            plugin.process_data(self._data)
        except Exception as error:  # pylint: disable=broad-except
            # broad exception on purpose because we do not know which exceptions might be thrown by an plugin
            # created by someone else
            UserInformation().inform(
                f"An error occured inside your plugin {plugin_class.name()}: {str(error)}\n"
                f"Try to debug by setting a breakpoint in your plugin {plugin_class.name()}."
            )
            return False

        return True

    def process_data(self, data: GlobalData):
        self._data = data
        self.exec_()
