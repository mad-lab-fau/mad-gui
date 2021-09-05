.. _customization:

*************
Customization
*************

Here we describe how you can:

- add a plugin to load data of a specific system / a specific format, implement a custom algorithm, and export data in a custom format
- create custom labels
- customize settings

.. note::
   In case you are not familiar with PyCharm and virtual environments, you might first want to check out our
   :ref:`Developer guidelines <developer guidelines>`.

Creating an executable script
#############################
Create a new project with a python file named `start_gui`.
Insert the following code:

.. code-block:: python

    from mad_gui import start_gui
    start_gui(data_dir=<put a directory here as string, e.g. "/home" or "C:/">)

You can execute this script as described in our :ref:`Developer guidelines <adding a script for execution>`.

.. _other systems:

Adding your plugins
###################

Adding support for other systems
********************************

The GUI can be imported into your python project and then you can inject `Importers`, `Algorithms`, and
`Exporters`.
Below we explain, how you can create and inject plugins for the GUI.
In case you want to give some feedback to the user via a popup you can use this:

.. code-block:: python

   from mad_gui.user_information import UserInformation
   UserInformation.ask_user("Your message")

.. note::
   You do not have to implement all methods of the regarding base class (BaseImporter, BaseAlgorithm, or BaseExporter),
   just the ones you need.

Implement an importer
*********************
If the user presses the `Load data` button in the GUI, a `LoadDataWindow <https://github.com/mad-lab-fau/mad-gui/blob/main/mad_gui/components/dialogs/plugin_selection/load_data_dialog.py#L28>`_
will pop up, as shown in our `exemplary video about loading data <https://youtu.be/akxcuFOesC8>`_.
In there, the user can select one of the importers that were passed to the GUI at startup by selecting it in a dropdown.
The loader takes care for:

   * transforming data from your recording system to a dictionary using its :meth:`~mad_gui.plugins.BaseImporter.load_sensor_data`
   * loading annotations from a user format using its :meth:`~mad_gui.plugins.BaseImporter.load_annotations`

Your `Importer` might make use of the methods already implemented in :class:`~mad_gui.plugins.BaseImporter`, which all Importers should inherit
from.

Here you can see an example of how to create an Importer and how to inject it:

.. code-block:: python

    from typing import Tuple, Dict
    from mad_gui import start_gui, BaseImporter

    class CustomImporter(BaseImporter):
        @classmethod
        def name(cls) -> str:
            # This will be shown as string in the dropdown menu of the LoadDataWindow upon
            # pressing the button "Load Data" in the GUI
            return "Custom importer"

        def load_sensor_data(self, file) -> Tuple[Dict, float]:
            # We create a dictionary with one key for each plot we want to generate.
            # Each value of the dictionary is a pandas dataframe, with columns being the single data streams /
            # sensor channels.
            data = <some method to load the data from file or relative to file>
            return {
                "left_sensor": data["left_foot"],
                "right_sensor": data["right_foot"],
            }, 204.8

    start_gui(
        data_dir=".", # you can also put a directory of your choice here, e.g. "/home" or "C:/"
        plugins=[CustomImporter],
    )


Implement an algorithm
**********************
If the user presses the `Use algorithm` button in the GUI, a `PluginSelectionDialog <https://github.com/mad-lab-fau/mad-gui/blob/main/mad_gui/components/dialogs/plugin_selection/plugin_selection_dialog.py#L22>`_
will pop up, as shown in our `exemplary video about automated annotations <https://youtu.be/VWQKYRRRGVA?t=65>`_
In there, the user can select one of the algorithms that were passed to the GUI at startup by selecting it in a dropdown.
The algorithm receives the plotted data as well as currently plotted labels, as kept in the `Global Data <https://mad-gui.readthedocs.io/en/latest/modules/generated/mad_gui/mad_gui.models.GlobalData.html#mad_gui.models.GlobalData>`_ object,
namely in its `Plot Data <https://mad-gui.readthedocs.io/en/latest/modules/generated/mad_gui/mad_gui.models.local.PlotData.html#mad_gui.models.local.PlotData>`_ objects.

Here you can see an example of how to create an algorithm that creates labels, that have the name `Activity`.
It is important, that we also pass a label to the GUI, which has the attribute `name = "Activity"`. Otherwise the GUI
will not know, what the label "Activity" should look like. Read more about creating custom labels :ref:`below <custom labels>`.

.. code-block:: python

    from typing import Tuple, Dict
    from mad_gui import start_gui, BaseAlgorithm

    class CustomAlgorithm(BaseAlgorithm):
        @classmethod
        def name(cls):
            return "Find Resting Phases (example MaD GUI)"

        def process_data(self, data: Dict[str, PlotData]) -> Dict[str, PlotData]:
            for sensor_plot in data.values():
                # sensor_plot.annotations["Activity"] basically is a pd.DataFrame.
                # However, we changed it to a custom object, which makes it easier for us internally to synchronize
                # our PlotData / GlobalData with the currently displayed data. Therefore, you can see the additional
                # `.data` in the next line.
                # You do not need to care about that, just make sure that the method `self.get_annotations(...)
                # returns a pd.DataFrame.
                sensor_plot.annotations["Activity"].data = self.get_annotations(sensor_plot.data


    class Activity(BaseRegionLabel):
        name = "Activity"
        min_height = 0.8
        max_height = 1

    start_gui(
        data_dir=".", # you can also put a directory of your choice here, e.g. "/home" or "C:/"
        plugins=[CustomAlgorithm],
        labels=[Activity]
    )

If you want to see a full example, head to `ExampleImporter <https://github.com/mad-lab-fau/mad-gui/blob/main/mad_gui/plugins/example.py#L29>`_

Implement an exporter
*********************
This basically works as described in the section of creating an importer.
Upon pressing the `Export data` button in the GUI, the `ExportResultsDialog <https://github.com/mad-lab-fau/mad-gui/blob/main/mad_gui/components/dialogs/plugin_selection/export_results_dialog.py#L19>`_ will be
opened, in which your exporter can be selected. Basically, you will receive a `GlobalData <https://mad-gui.readthedocs.io/en/latest/modules/generated/mad_gui/mad_gui.models.GlobalData.html#mad_gui.models.GlobalData>`_ object, which keeps
all the data form the GUI and you can process / export it in whatever way you want:

.. code-block:: python

    from typing import Tuple, Dict
    from mad_gui import start_gui, BaseExporter, BaseSettings

    class CustomExporter(BaseImporter):
        @classmethod
        def name(cls) -> str:
            # This will be shown as string in the dropdown menu of mad_gui.components.dialogs.ExportResultsDialog upon
            # pressing the button "Export data" in the GUI
            return "Custom exporter"

        def process_data(global_data):
            # Here you can do whatever you like with our global data.
            # See the API Reference for more information about our GlobalData object

After creating your exporter, make sure to also pass it to the `start_gui` function.

Setting a Theme
###############

.. code-block:: python

   from mad_gui.config import BaseTheme
   from PySide2.QtGui import QColor

   class MyTheme(BaseTheme):
     COLOR_DARK = QColor(0, 56, 101)
     COLOR_LIGHT = QColor(144, 167, 198)

   start_gui(
    theme=MyTheme,
   )


.. _setting constants:

Setting Constants
#################

You can create your own settings by creating a class, which inherits from our `BaseSettings <https://github.com/mad-lab-fau/mad-gui/blob/main/mad_gui/config/settings.py#L1>`_.
The following example makes use of the BaseSettings and simply overrides some properties:

.. code-block:: python

   from mad_gui.config import BaseSettings

   class MySettings(BaseSettings):
     CHANNELS_TO_PLOT = ["acc_x", "acc_z"]

     # used if a label has `snap_to_min = True` or `snap_to_max = True`
     SNAP_AXIS = "acc_x"
     SNAP_RANGE_S = 0.2

     # Set the width of IMU plot to this, when hitting the play button for the video.
     PLOT_WIDTH_PLAYING_VIDEO = 20  # in seconds

   start_gui(
    settings=MySettings,
   )

.. _custom labels:

Creating custom labels
######################
You can create labels and pass them to our GUI.
Your label must inherit form our `BaseRegionLabel <https://mad-gui.readthedocs.io/en/latest/modules/generated/plot_tools/mad_gui.plot_tools.BaseRegionLabel.html#mad_gui.plot_tools.BaseRegionLabel>`_.
It could for example look like this:

.. code-block:: python

   from mad_gui.plot_tools.base_label import BaseRegionLabel
   from mad_gui import start_gui

   class Status(BaseRegionLabel):
      # This label will always be shown at the lowest 20% of the plot view
      min_height = 0
      max_height = 0.2
      name = "Anomaly Label"
      # Snapping will be done on the axis and in the range defined in MySettings (see above)
      snap_to_min = True
      # snap_to_max = False  # if setting this to `True`, set `snap_to_min` to `False` or delete it
      descriptions = {"normal": None, "anomaly": ["too fast", "too slow"]}

   start_gui(labels=[Status])

The `description` defines the possible strings that can be assigned to a label. They will automatically show up after
adding a new label or by clicking on a label when in `Edit label` mode, such that the user can select one of the
descriptions. In our `exemplary video <https://www.youtube.com/watch?v=VWQKYRRRGVA&t=18s>`_, this is
`{"stand": None, "walk": ["fast", "slow"], "jump": None}`.
