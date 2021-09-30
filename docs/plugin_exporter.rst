.. sectnum::

.. _implement exporter:

********
Exporter
********

Export displayed annotations
############################

This basically works as described in the section of creating an importer.
Upon pressing the `Export data` button in the GUI, the `ExportResultsDialog <https://github.com/mad-lab-fau/mad-gui/blob/main/mad_gui/components/dialogs/plugin_selection/export_results_dialog.py#L19>`_ will be
opened, in which your exporter can be selected. Basically, you will receive a `GlobalData <https://mad-gui.readthedocs.io/en/latest/modules/generated/mad_gui/mad_gui.models.GlobalData.html#mad_gui.models.GlobalData>`_ object, which keeps
all the data form the GUI and you can process / export it in whatever way you want:

.. code-block:: python

    from mad_gui import start_gui, BaseExporter, BaseSettings
    from mad-gui.models import GlobalData

    class CustomExporter(BaseExporter):
        @classmethod
        def name(cls) -> str:
            # This will be shown as string in the dropdown menu of
            # mad_gui.components.dialogs.ExportResultsDialog upon pressing
            # the button "Export data" in the GUI
            return "Custom exporter"

        def process_data(self, global_data: GlobalData):
            # Here you can do whatever you like with our global data.
            # See the API Reference for more information about our GlobalData object

After creating your exporter, make sure to also pass it to the `start_gui` function.