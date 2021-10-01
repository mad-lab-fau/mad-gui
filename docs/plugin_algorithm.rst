.. sectnum::

.. _implement algorithm:

*********
Algorithm
*********

Overview
########

The basic implementation of an algorithm is explained in this section. You have two possibilities:

- calculate features for existing annotations (see 00:50 in the video below)
- create annotations using an algorithm (see 00:40 in the video below)

The will be able to select your plugin it after pressing the `Use algorithm`.

.. raw:: html

   <iframe width="560" height="315" src="https://www.youtube.com/embed/VWQKYRRRGVA?start=3" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

Create a file that will include your custom algorithm
#####################################################

.. image:: _static/images/development/algorithm_create_file.png
    :alt: Creating a file for the plugin
    :height: 250

.. _algorithm class:

Develop your custom algorithm in that file
##########################################

Use this code snippet and

- set the algorithm's name as return value of the regarding method
- fill `process_data` and potentially a helper method as described in the next sections

.. code-block:: python

    """This is the content of custom_algorithm.py, which holds my first algorithm plugin."""

    from typing import Dict
    import pandas as pd
    from mad_gui import start_gui, BaseAlgorithm
    from mad_gui.plot_tools.labels import BaseRegionLabel
    from mad_gui.models.local import PlotData
    from mad_gui.components.dialogs.user_information import UserInformation

    class CustomAlgorithm(BaseAlgorithm):
        @classmethod
        def name(cls):
            ###################################################################
            ### This is the string that will show up in the GUI's dropdown, ###
            ###        after pressing the `Use algorithm` button.           ###
            ###################################################################
            return "Find Resting Phases (example MaD GUI)"

        # The content of this method can be as described in the two sections Option A and Option B below
        def process_data(self, data: Dict[str, PlotData]) -> Dict[str, PlotData]:
            #######################################################################
            # ----> See sectionx 3, 3.1, and 3.2 for content of this method <---- #
            #######################################################################

When you have put this code into `custom_algorithm.py`, go on with the next sections to see what code needs to go into
`process_data`.
If you want to know more about the data type `Plot Data`, please refer to
`the regarding documentation <https://mad-gui.readthedocs.io/en/latest/modules/generated/mad_gui/mad_gui.models.local.PlotData.html#mad_gui.models.local.PlotData>`_.



Fill the method `process_data` with content
###########################################

The above code snippet misses the content of `process data`. Depending on whether you want your algorithm to calculate
features from existing annotations or to create annotations for the plotted data, the content of your plugin's **`process_data`**
will be as described in **either** :ref:`option a` **or** :ref:`option b`.


.. _option a:

Calculate features for existing annotations
*******************************************

.. note::

   This code snippet is to be inserted into your `CustomAlgorithm` from the section :ref:`algorithm class`.

This assumes, there are already annotations in the GUI, as shown in `this GIF <_static/gifs/algorithm_feature.gif>`_.
The existing annotations may have been plotted by an algorithm, or may have been added manually in the GUI by using the
`Add label` mode, both examples are shown in our `exemplary video about annotations <https://youtu.be/VWQKYRRRGVA">`_.

Using this custom algorithm, you can create information about each existing annotation in the plot.
The GUI will take care for showing the results as soon as the user hovers of the annotation with the mouse, as
you can see in the GIF we linked above.

You just need to put a string into each annotation's `description`, as shown in the code snippet below:

.. code-block:: python

   def process_data(self, data: Dict[str, PlotData]) -> Dict[str, PlotData]:
      for sensor_plot in data.values():
          if len(sensor_plot.annotations["Activity"].data) == 0:
            UserInformation.inform("There are no annotations in the plot, therefore nothing is analyzed.")
          for i_activity, activity in sensor_plot.annotations["Activity"].data.iterrows():
              activity_sensor_data = sensor_plot.data.iloc[activity.start:activity.end]
              sensor_plot.annotations["Activity"].data.at[
                  i_activity, 'description'
              ] = self.calculate_features(activity_sensor_data,
                                          sensor_plot.sampling_rate_hz
                                         )
         UserInformation.inform("Algorithm executed. Move the mouse over a label to see the result in a pop-up.")

   @staticmethod
   def calculate_features(sensor_data: pd.DataFrame, sampling_rate_hz: float) -> str:
      ##############################################################################
      ###                               README                                   ###
      ###    Here you can use a more complex algorithm to calculate features.    ###
      ###   Please format your algorithm's results as a string and               ###
      ###                           RETURN A STRING.                             ###
      ##############################################################################
      return f"Mean value acc_x = {sensor_data['acc_x'].mean()}"


.. _option b:

Create annotations to be plotted
********************************

.. note::

   This code snippet is to be inserted into your `CustomAlgorithm` from the section :ref:`algorithm class`.

A plugin like this can be used to create annotations which span a region between to samples given by your algorithm.
After returning from `process_data`, the GUI will plot the annotations automatically for you, as shown in
`this GIF <_static/gifs/algorithm_label.gif>`_.

In the code snippet below, line 6 `sensor_plot.annotations["Exemplary Label"]` basically is a `pd.DataFrame`.
However, you can see an additional `.data` in the code. This is due to internal data handling in the GUI.
You do not need to care about that, just make sure that the method `self.create_annotations(...)`
returns a pd.DataFrame with the columns `start` and `end`.

.. code-block:: python
   :linenos:

   def process_data(self, data: Dict[str, PlotData]) -> Dict[str, PlotData]:
     for plot_name, sensor_plot in data.items():
         # Use the currently plotted data to create annotations, like an MyLabel Label
         annotations = self.create_annotations(sensor_plot.data, sensor_plot.sampling_rate_hz)
         UserInformation.inform(f"Found {len(annotations)} for {plot_name}.")
         sensor_plot.annotations["Exemplary Label"].data = annotations

   @staticmethod
   def create_annotations(sensor_data: pd.DataFrame, sampling_rate_hz: float) -> pd.DataFrame:
     """Some code that creates a pd.DataFrame with the columns `start` and `end`.

     Each row corresponds to one annotation to be plotted.
     """
     #########################################################################
     ###                                 README                            ###
     ### Here you create a dataframe, which has the columns start and end. ###
     ### For each of the columns, the GUI will then plot one annotation.   ###
     #########################################################################
     starts = # must be a list
     ends = # must be a list
     annotations = pd.DataFrame(data=[starts, ends], columns = ['start', 'end'])
     return annotations

Pass algorithm to the GUI
#########################

.. note:: You may pass several plugins like so: `start_gui(pluings=[MyFirstPlugin, MySecondPlugin])`

.. code-block:: python

   from custom_algorithm import CustomAlgorithm
   from mad_gui import start_gui

   start_gui(plugins=[MyAlgorithm])
