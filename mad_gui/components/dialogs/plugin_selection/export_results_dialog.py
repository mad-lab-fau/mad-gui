from PySide2 import QtCore
from PySide2.QtUiTools import loadUiType

from mad_gui import BaseExporter
from mad_gui.components.dialogs.user_information import UserInformation
from mad_gui.components.helper import set_cursor
from mad_gui.models.global_data import GlobalData, PlotData
from mad_gui.qt_designer import UI_PATH
from mad_gui.utils.helper import resource_path
from typing import List, Type

ui_path = resource_path(str(UI_PATH / "export.ui"))
if ".ui" in ui_path:
    PluginSelectorWindow, _ = loadUiType(ui_path)
elif ".py" in ui_path:
    from mad_gui.qt_designer.build.export import Ui_Form as PluginSelectorWindow  # pylint: disable=C0412,E0401


class ExportResultsDialog(PluginSelectorWindow):
    """A dialog to select the exporter to use to export results from the shown data and labels.

    See Also
    --------
    :class:`~mad_gui.windows.BasePluginSelector`

    """

    _data: PlotData

    def __init__(self, exporters: List[Type[BaseExporter]], parent=None):
        super().__init__()
        self.exporters = exporters
        self.parent = parent
        self.ui = PluginSelectorWindow()
        self.setWindowIcon(parent.windowIcon())
        self.ui.setupUi(self)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Export Results")
        self.ui.combo_plugin.addItems([exporter.name() for exporter in self.exporters])
        self.ui.btn_ok.clicked.connect(self.process_data)
        self.ui.btn_cancel.clicked.connect(self.close)

    def process_data(self):
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
        exporter_class = self.exporters[self.ui.combo_plugin.currentIndex()]
        try:
            # TODO: Implement loader config
            user_config = {}
            exporter = exporter_class(parent=self, **user_config)
        except Exception as e:  # pylint: disable=broad-except
            # broad exception on purpose because we do not know which exceptions might be thrown by an exporter
            # created by someone else
            UserInformation().inform("Error loading Plugin {}".format(exporter_class.name()))
            print(e)
            return False

        try:
            exporter.export(self._data)
        except Exception as e:  # pylint: disable=broad-except
            # broad exception on purpose because we do not know which exceptions might be thrown by an exporter
            # created by someone else
            UserInformation().inform("An error occured exporting the data")
            print(e)
            return False

        return True

    def export_data(self, data: GlobalData):
        self._data = data
        self.exec_()
