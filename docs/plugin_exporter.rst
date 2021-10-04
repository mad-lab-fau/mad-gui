.. sectnum::

.. _implement exporter:

********
Exporter
********

.. danger::

   In case you do not know how our GUI handles plugins, please take a quick look at the part
   `Developing Plugins <https://mad-gui.readthedocs.io/en/latest/README.html#developing-plugins>`_ in our Readme.

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
            # Here is an example on how to export all annotations and their descriptions:
            file = QFileDialog().getSaveFileName(
                None, "Save GUI data", str(Path(global_data.data_file).parent) + "/results.xlsx", "*.xlsx"
            )[0]
            writer = pd.ExcelWriter(file)
            for plot_name, plot_data in global_data.plot_data.items():
                for label_name, annotations in plot_data.annotations.items():
                    if len(annotations.data) == 0:
                        continue
                    annotations.data.to_excel(writer, sheet_name=label_name)

            writer.save()
            UserInformation.inform(f"The results were saved to {file}.")

After creating your exporter, make sure to also pass it to the `start_gui` function.