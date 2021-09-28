.. sectnum::

.. _customization:

***********
Development
***********

.. note::
   In case you experience issues, please try to find a solution in :ref:`Troubleshooting for Developers <troubleshooting developers>`.
   

About plugins (IMPORTANT)
*************************

You can create your own plugins as we describe it on this page.
If you want to make use of the specific plugin in the GUI, **you have to pass that plugin to our `start_gui` function.**
Your plugin will then receive data from our GUI, e.g. when your plugin was selected to load data or when it was
selected as an algorithm.

.. code-block:: python

    from mad_gui import start_gui
    start_gui(plugins=[MyImporter, MyAlgorithm])

.. note::
    You can execute such a script as described in our section :ref:`Prepare Development <adding a script for execution>`.

.. _other systems:

Adding your plugins
*******************

Below we explain, how you can create and inject such plugins to the GUI.
If - at any point - you want to send a message to the user of the GUI, you create a message box with an OK button like
this:

.. code-block:: python

   from mad_gui.user_information import UserInformation
   UserInformation.ask_user("Your message")

.. _implement importer:

Loading and displaying data using your custom importer
#######################################################

In the GIF you can see what the rough steps are.
You can find a more **detailed step-by-step explanation below the GIF**.

.. image:: _static/gifs/importer.gif
    :alt: Workflow for implementing an importer

If the user presses the `Load data` button in the GUI, a window for selecting the importer and data to be loaded
will pop up, as shown in the GIF and our `exemplary video about loading data <https://youtu.be/akxcuFOesC8>`_.
The user can select one of the importers that were passed to the GUI at startup by selecting it in a dropdown.


After the user presses `Start processing`, the path to the selected file will be passed to the selected loader's
`load_sensor_data` method.

**Steps to implement your importer (click to unfold/fold the sections):**

.. raw:: html

   <details>
   <summary>1. create a file that will include your custom importer, e.g. `custom_importer.py` <u><font color="#0000FF">(click to show image)</font></u></summary>

.. image:: _static/images/development/importer_create_file.png
    :alt: Creating a file for the plugin

.. raw:: html

   </details>

.. raw:: html

   <details>
   <summary>2. develop your custom importer in that file, as shown in this code snippet <u><font color="#0000FF">(click to show code)</font></u></summary>

.. code-block:: python

   """These are the contents of custom_importer.py, which holds my first importer."""

    from typing import Dict
    import pandas as pd
    from mad_gui import start_gui, BaseImporter

    class CustomImporter(BaseImporter):
        @classmethod
        def name(cls) -> str:
            ################################################
            ###                   README                 ###
            ### Set your importer's name as return value ###
            ### This name will show up in the dropdown.   ###
            ################################################
            return "My Importer"

        def load_sensor_data(self, file_path: str) -> Dict:
            ##################################################################
            ###                       README                               ###
            ### a) Use the argument `file_path` to load data. Transform    ###
            ###    it to a pandas dataframe (columns are sensor channels). ###
            ###    Assign it to sensor_data.                               ###
            ###                                                            ###
            ### b) load the sampling rate (int or float)                   ###
            ##################################################################
            sensor_data = 
            sampling_rate =

            # CAUTION: if you only want to have one plot you do not need to
            # change the following lines!
            # If you want several plots, just add another sensor like "IMU foot"
            # to the `data` dictionary.
            data = {
            "IMU Hip": {
                "sensor_data": sensor_data,
                "sampling_rate_hz": sampling_rate,
                }
            }

            return data

.. raw:: html

   </details>


.. raw:: html

   <details>
   <summary>3. pass it to the `start_gui` function <u><font color="#0000FF">(click to show image)</font></u></summary>

.. code-block:: python

   from mad_gui import start_gui
   from custom_importer import CustomImporter

   start_gui(plugins=[CustomImporter])

.. image:: _static/images/development/importer_pass_to_gui.png
    :alt: Making the plugin available in the GUI

.. raw:: html

   </details>
   <br />

Now you can select the importer in the GUI by pressing `Load Data` and then selecting it in the dropdown on the upper
left in the pop-up window.

.. note::
    In case loading your file does not work, we recommend to set breakpoints into your loader and check, whether
    everything does what you expect it to do. Also you might want to look at our section about
    :ref:`Troubleshooting development <troubleshooting development>` or at
    `load_sensor_data's documentation <https://mad-gui.readthedocs.io/en/latest/modules/generated/plugins/mad_gui.plugins.BaseImporter.html#mad_gui.plugins.BaseImporter.load_sensor_data>`_.

.. _implement algorithm:

Create annotations or calculate features for existing annotations
##################################################################

If the user presses the `Use algorithm` button in the GUI, a `PluginSelectionDialog <https://github.com/mad-lab-fau/mad-gui/blob/main/mad_gui/components/dialogs/plugin_selection/plugin_selection_dialog.py#L29>`_
will pop up, as shown in our `exemplary video about automated annotations <https://youtu.be/VWQKYRRRGVA?t=65>`_.
In there, the user can select one of the algorithms that were passed to the GUI at startup by selecting it in a dropdown.
The algorithm receives `Global Data <https://mad-gui.readthedocs.io/en/latest/modules/generated/mad_gui/mad_gui.models.GlobalData.html#mad_gui.models.GlobalData>`_'s
plot_data dictionary, where the keys are the plot names and the values are of type
`Plot Data <https://mad-gui.readthedocs.io/en/latest/modules/generated/mad_gui/mad_gui.models.local.PlotData.html#mad_gui.models.local.PlotData>`_.
Below we show you what that means and how you can use this data.

The general structure of your algorithm-class will look as shown below.
The content of `process_data`, however, depends on the exact use-case of the algorithm.
Two possible use-cases are explained in the subsections after this code snippet.


.. code-block:: python

    from typing import Dict
    import pandas as pd
    from mad_gui import start_gui, BaseAlgorithm
    from mad_gui.plot_tools.labels import BaseRegionLabel
    from mad_gui.models.local import PlotData
    from mad_gui.components.dialogs.user_information import UserInformation

    class CustomAlgorithm(BaseAlgorithm):
        @classmethod
        def name(cls):
            return "Find Resting Phases (example MaD GUI)"

        # The content of this method can be as described in the two sections Option A and Option B below
        def process_data(self, data: Dict[str, PlotData]) -> Dict[str, PlotData]:
            #####################################################################
            # ----> See the two sections below for content of this method <---- #
            #####################################################################

    # It is important to create the class Activity and pass it to the GUI because otherwise
    # the sensor_plot.annotation will not have a key `Activity` and thus won't know how to plot
    # the labels it receives from CustomAlgorithm.process_data via its process_data method
    class Activity(BaseRegionLabel):
        name = "Activity Label"
        min_height = 0
        max_height = 0.8

    start_gui(
        data_dir=".", # you can also put a directory of your choice here, e.g. "/home" or "C:/"
        plugins=[CustomAlgorithm],
        labels=[Activity]
    )

In this example we are using the label class `Activity`, however, you can also use custom labels.
If you want to read more about creating custom labels, see :ref:`below <custom labels>`.
If you want to see a full working example, head to `ExampleImporter <https://github.com/mad-lab-fau/mad-gui/blob/main/mad_gui/plugins/example.py#L29>`_.

.. _option a:

Option A: Create labels to be plotted
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create labels which span a region between to samples given by your algorithm. After you return from `process_data`, the
GUI will plot the labels automatically for you, as shown in this image (click to zoom):

.. image:: _static/images/development/algorithm_labelling.png
    :alt: Automated labelling by a plugin-algorithm
    :height: 200



.. note::

   This code snippet is to be inserted into your `CustomAlgorithm` as explained in :ref:`implement algorithm`.
   The labels you want to create (in this case `Activity`) must have been passed to the `start_gui` method on startup.

In the code snippet below, line 6 `sensor_plot.annotations["Activity"]` basically is a `pd.DataFrame`.
However, you can see an additional `.data` in the code. This is due to internal data handling in the GUI.
You do not need to care about that, just make sure that the method `self.create_annotations(...)`
returns a pd.DataFrame with the columns `start` and `end`.

.. code-block:: python
   :linenos:

    def process_data(self, data: Dict[str, PlotData]) -> Dict[str, PlotData]:
        for sensor_plot in data.values():
            # Use the currently plotted data to create labels, like an Activity Label
            annotations = self.create_annotations(sensor_plot.data, sensor_plot.sampling_rate_hz)
            UserInformation.inform(f"Found {len(annotations)} resting phases.")
            sensor_plot.annotations["Activity Label"].data = annotations

    @staticmethod
    def create_annotations(sensor_data: pd.DataFrame, sampling_rate_hz: float) -> pd.DataFrame:
        """Some code that creates a pd.DataFrame with the columns `start` and `end`.

        Each row corresponds to one label to be plotted.
        """
        # use some algorithm to find out where activities should start
        # like `running`
        starts = ...
        # ...and the same for ends of the activity
        ends = ...
        annotations = pd.DataFrame(data=[starts, ends], columns = ['start', 'end'])
        return annotations

.. _option_b:

Option B: Analyze data within existing labels
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create information about each existing label/annotation in the plot.
The existing labels maybe were plotted by an algorithm, as shown in :ref:`option a`, or maybe they were added manually
in the GUI by using the `Add label` mode.

To show some results for each of the annotations, you just need to put a string into each label's `description`, as
shown in the code snippet below.
The GUI will automatically take care for showing that string when the user hovers over a label, as shown in this image
(click to zoom):

.. image:: _static/images/development/algorithm_analyzing.png
    :alt: Automated analysis by a plugin-algorithm
    :height: 200

.. note::

   This code snippet is to be inserted into your `CustomAlgorithm` as explained in :ref:`implement algorithm`.

.. code-block:: python

   from mad_gui.components.dialogs import UserInformation

   def process_data(self, data: Dict[str, PlotData]) -> Dict[str, PlotData]:
      for sensor_plot in data.values():
          if len(sensor_plot.annotations["Activity"]) == 0:
            UserInformation.inform("There are no labels in the plot, therefor nothing is analyzed")
          for i_activity, activity in sensor_plot.annotations["Activity"].data.iterrows():
              # use some method to calculate features for each labelled activity
              # the resulting string will be the activity label's tool tip,
              # so it can be seen by the user by hovering over the label with the mouse
              sensor_plot.annotations["Activity"].data.at[
                  i_activity, 'description'
              ] = self.calculate_features(sensor_plot.data.iloc[activity.start:activity.end],
                                          sensor_plot.sampling_rate_hz
                                         )

   @staticmethod
   def calculate_features(sensor_data: pd.DataFrame, fs: sampling_rate_hz) -> str:
      # here you can for example use an algorithm to calculate features of the data.
      # you can also inform the user about things you like using a pop-up window:
      UserInformation.inform(f"Calculating a feature for data between the samples"
                             f" {sensor_data.index.iloc[0]} and"
                             f" {sensor_data.index.iloc[-1]}")
      return f"Mean value acc_x = {sensor_data['acc_x'].mean()}"

Export data
###########
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
***************

You can easily change the two dominating colors by passing your own theme to the GUI.

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
*****************

You can create your own settings by creating a class, which inherits from our `BaseSettings <https://github.com/mad-lab-fau/mad-gui/blob/main/mad_gui/config/settings.py#L1>`_.
The following example makes use of the BaseSettings and simply overrides some properties:

.. code-block:: python

   from mad_gui.config import BaseSettings

   class MySettings(BaseSettings):
     CHANNELS_TO_PLOT = ["acc_x", "acc_z"]

     # used if a label has `snap_to_min = True` or `snap_to_max = True`
     SNAP_AXIS = "acc_x"
     SNAP_RANGE_S = 0.2

     # in all your labels you can add an event by using `Ctrl` as modifier when in `Add label` mode
     # when adding an event the user will be prompted to select one of these two strings as a `description` for the event
     EVENTS = ["important event", "other type of important event"]

     # Set the width of IMU plot to this, when hitting the play button for the video.
     PLOT_WIDTH_PLAYING_VIDEO = 20  # in seconds

     # If plotting large datasets, this speeds up plotting, however might result in inaccurate representation of the data
     AUTO_DOWNSAMPLE = True

   start_gui(
    settings=MySettings,
   )

.. _custom labels:


Creating custom labels
**********************
You can create labels and pass them to our GUI.
Your label must inherit form our `BaseRegionLabel <https://mad-gui.readthedocs.io/en/latest/modules/generated/plot_tools/mad_gui.plot_tools.labels.BaseRegionLabel.html#mad_gui.plot_tools.labels.BaseRegionLabel>`_.
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

      # User will be asked to set the label's description when creating a label.
      # This can have an arbitrary amount of levels with nested dictionaries.
      descriptions = {"normal": None, "anomaly": ["too fast", "too slow"]}

   start_gui(labels=[Status])

The `description` defines the possible strings that can be assigned to a label. They will automatically show up after
adding a new label or by clicking on a label when in `Edit label` mode, such that the user can select one of the
descriptions. In our `exemplary video <https://www.youtube.com/watch?v=VWQKYRRRGVA&t=18s>`_, this is
`{"stand": None, "walk": ["fast", "slow"], "jump": None}`.

