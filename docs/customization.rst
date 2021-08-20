.. _customization:

*************
Customization
*************

Here we describe how you can:

- load data from a specific system
- implement an algorithm from another python package
- customize settings

However, in case you want to change something closer at the core of the GUI, you might need to take a look at our
:ref:`Contribution guidelines <contribution guidelines>`.

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

The GUI can be imported into your python project and then you can inject `Importers`, `Algorithms` (to be done), and
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
If the user presses the `Load data` button in the GUI, a new window will pop up (`LoadDataWindow <https://github.com/mad-lab-fau/mad-gui/blob/main/mad_gui/components/dialogs/plugin_selection/load_data_dialog.py#L28>`_).
In there, the user can select one of the importers that were passed to the GUI at startup by selecting it in a dropdown.
The loader takes care for:

   * transforming data from your recording system to a dictionary using its :meth:`~mad_gui.plugins.BaseImporter.load_sensor_data`
   * loading annotations from a user format using its :meth:`~mad_gui.plugins.BaseImporter.load_annotations`

Your `Importer` might make use of the methods already implemented in :class:`~mad_gui.plugins.BaseImporter`, which all Importers should inherit
from.

Here you can see an example of how to create an Importer and how to inject it:

.. code-block:: python

    from typing import Tuple, Dict
    from mad_gui import start_gui, BaseImporter, BaseSettings

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

This created Importer can be accessed in the GUI by clicking the `Load Data` button, which in turn opens the
`LoadDataWindow <https://github.com/mad-lab-fau/mad-gui/blob/main/mad_gui/components/dialogs/plugin_selection/load_data_dialog.py#L28>`_.

If you want to also add algorithms which are executed upon pressing the buttons `Use algorithm` and `Export Data`,
please see the two following sections.

Implement an algorithm (`Use Algorithm` button)
***********************************************
If you want to implement an algorithm to automatically create labels based on the displayed data,
you will have to additionally implement your custom loader's :meth:`~mad_gui.plugins.BaseImporter.annotation_from_data`
method.

Implement an exporter (`Export data` button)
********************************************
This basically works as described in the section of creating an importer.
Upon pressing the `Export data` button in the GUI, the `ExportResultsDialog <https://github.com/mad-lab-fau/mad-gui/blob/main/mad_gui/components/dialogs/plugin_selection/export_results_dialog.py#L19>`_ will be
opened, in which your exporter can be selected.

.. code-block:: python

    from typing import Tuple, Dict
    from mad_gui import start_gui, BaseExporter, BaseSettings

    class CustomExporter(BaseImporter):
        @classmethod
        def name(cls) -> str:
            # This will be shown as string in the dropdown menu of mad_gui.components.dialogs.ExportResultsDialog upon
            # pressing the button "Export data" in the GUI
            return "Custom exporter"

After creating your exporter, make sure to also pass it to the `start_gui` function.


Setting Constants
#################

You can create your own settings by creating a class, which inherits from our BaseSettings.
Below show an example for all the things you can customize.


Axes to plot
************
Those are the axes which are plotted by default after loading data.
However, you can change that at runtime by right-clicking on a graph and then go to the submenu "Select Axes".
Note that the axis names need to fit the axis names that are in the loaded data.

.. code-block:: python

   AXES_TO_PLOT = [
       "acc_x",
       "gyr_y"
   ]

.. _consts activity labels:

Activity labels
***************
After adding an activity, there will be a pop-up window, which gives you the possiblity to assign one of the following
activity types to it. Furthermore, you can select those labels, for which you additionally want to provide details in
a separate pop-up window.

.. code-block:: python

   ACTIVITIES = [
       "sitting",
       "moving"
   ]
   DETAILS = ["walk", "run"]  # options for details, if user selected activity_type2 before

.. _consts-stride-labels:

Standard plot width
*******************
Set the width of IMU plot to this, when hitting the play button for the video.

.. code-block:: python

   PLOT_WIDTH_PLAYING_VIDEO = 20  # in seconds


Creating custom labels
######################
You can create labels and pass them to our GUI.
Your label must inherit form our BaseLabel.
It could for example look like this:

.. code-block:: python

   from mad_gui.plot_tools.base_label import BaseRegionLabel
   from mad_gui import start_gui

   class Anomaly(BaseRegionLabel):
      # This label will always be shown at the lowest 20% of the plot view
      min_height = 0
      max_height = 0.2
      name = "Anomaly Label"

   start_gui(labels=[Anomaly])