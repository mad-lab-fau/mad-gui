.. sectnum::

.. _implement algorithm:

*********
Algorithm
*********

Overview
########

First of all you need to create a file, which will keep
your algorithm, as shown in `this image <_static/images/development/algorithm_create_file.png>`_.
Then you can implement your algorithm based on one of the two examples we give below.

.. warning::

   Depending on what your algorithm should do, you will need only one of the two subsections below.

- 1.2 Algorithm, which creates features for existing annotations:

   - see what that means `in a video <https://www.youtube.com/watch?v=VWQKYRRRGVA&t=9s>`_ (00:40 to 00:50)
   - use the :ref:`code example <algorithm annotations>`

- 1.3 Algorithm, which creates features for existing annotations:

   - see what that means `in a video <https://www.youtube.com/watch?v=VWQKYRRRGVA&t=9s>`_ (00:50 to 01:00)
   - use the :ref:`code example <algorithm features>`

The user will be able to select your plugin after pressing the button `Use algorithm`, as shown in our
`exemplary video <https://www.youtube.com/watch?v=VWQKYRRRGVA>`_.

.. _algorithm annotations:

Algorithm, which creates annotations to be plotted
##################################################

A plugin like this can be used to create annotations which span a region between to samples.
Your algorithm may for example be able to find regions where the sensor was not moving.
The GUI will plot the annotations automatically after it returns from your algorithm's `process_data` method.
You can see an example in `this GIF <_static/gifs/algorithm_label.gif>`_.

.. admonition:: Getting started quickly
   :class: tip

   The code snippet below is a working example. To adapt it to your use case, you only need to modify the methods
   **name** and **calculate_features**.

Only in case you are passing labels to our GUI using like `start_gui(labels=[MyCustomLabel, MyOtherCustomLabel])`,
you need to change something in `process_data` in case. For a first try, we recommend to NOT pass labels!

If you want to know more about the data type `Plot Data`, which you will receive as an argument, please refer to
`the regarding documentation <https://mad-gui.readthedocs.io/en/latest/modules/generated/mad_gui/mad_gui.models.local.PlotData.html#mad_gui.models.local.PlotData>`_.
However, we assume you can get along with this code snippet and without reading something about `Plot Data`:

.. code-block:: python

    """This is the content of custom_algorithm.py, which holds my first algorithm plugin."""

    import warnings
    from typing import Dict
    import pandas as pd
    from mad_gui import BaseAlgorithm
    from mad_gui.models.local import PlotData
    from mad_gui.components.dialogs.user_information import UserInformation

    class CustomAlgorithm(BaseAlgorithm):
        @classmethod
        def name(cls) -> str:
            name = "Algorithm to do ..."
            warnings.warn("Please give you algorithm a meaningful name.")
            return name

    def process_data(self, data: Dict[str, PlotData]):
        for plot_name, sensor_plot in data.items():
            # Use the currently plotted data to create annotations
            annotations = self.create_annotations(sensor_plot.data, sensor_plot.sampling_rate_hz)
            UserInformation.inform(f"Found {len(annotations)} for {plot_name}.")
            sensor_plot.annotations["Activity"].data = annotations

    @staticmethod
    def create_annotations(sensor_data: pd.DataFrame, sampling_rate_hz: float) -> pd.DataFrame:
        """Some code that creates a pd.DataFrame with the columns `start` and `end`.

        Each row corresponds to one annotation to be plotted.
        """
        #########################################################################
        ###                                 README                            ###
        ### Here you create a dataframe, which has the columns start and end. ###
        ###  For each of the columns, the GUI will then plot one annotation.  ###
        ###               You could for example do something like             ###
        ###     starts, ends = my_algorithm_to_find_regions(sensor_data)      ###
        #########################################################################
        starts = [int(0.1 * len(data)), int(0.5 * len(data))] # must be a list
        ends = [int(0.4 * len(data)), int(0.9) * len(data))] # must be a list

        warnings.warn("Using exemplary labels, please find starts and ends on your own.")

        annotations = pd.DataFrame(data=[starts, ends], columns = ['start', 'end'])
        return annotations

.. admonition:: Using your algorithm in the GUI
   :class: tip

    As a last step, you need to pass the algorithm (and optionally other plugins) to the start_gui
    function, see :ref:`Pass algorithm to the GUI <pass algorithm>`.

.. _algorithm features:

Algorithm, which creates features for existing annotations
##########################################################

A plugin like this can be used to calculate features for annotations that are already visible in the GUI.
For example the user might have created annotations manually or by using an algorithm as described in :ref:`algorithm annotations`.

Now, you might want to know the mean value of the sensor signal in each of the annotated regions.
For this task you can create an algorithm as we describe it in this section.
After execution of the algorithm, the GUI will take care for showing the results as soon as the user hovers of the
annotation with the mouse, as you can see in `this GIF <_static/gifs/algorithm_feature.gif>`_.

You can copy and paste the code snippet into your file for an algorithm.
If you want to know more about the data type `Plot Data`, which you will receive as an argument, please refer to
`the regarding documentation <https://mad-gui.readthedocs.io/en/latest/modules/generated/mad_gui/mad_gui.models.local.PlotData.html#mad_gui.models.local.PlotData>`_.
However, we assume you can get along with this code snippet and without reading something about `Plot Data`:

.. admonition:: Getting started quickly
   :class: tip

   The code snippet below is a working example. To adapt it to your use case, you only need to modify the methods
   **name** and **calculate_features**.

Only in case you are passing labels to our GUI using like `start_gui(labels=[MyCustomLabel, MyOtherCustomLabel])`,
you need to change something in `process_data` in case. For a first try, we recommend to NOT pass labels!

.. code-block:: python

    """This is the content of custom_algorithm.py, which holds my first algorithm plugin."""

    import warnings
    from typing import Dict
    import pandas as pd
    from mad_gui import BaseAlgorithm
    from mad_gui.models.local import PlotData
    from mad_gui.components.dialogs.user_information import UserInformation

    class CustomAlgorithm(BaseAlgorithm):
        @classmethod
        def name(cls) -> str:
            name = "Algorithm to do ..."
            warnings.warn("Please give you algorithm a meaningful name.")
            return name

        def process_data(self, data: Dict[str, PlotData]):
            """Calculate a feature for all annotations of type "Activity" that exist in the plots.

            This method automatically receives the plotted data and annotations from the plot,
            as soon as the user presses the `Use Algorithm` button and selects this algorithm.
            """
            # iterate over all existing plots
            for plot_name, plot_data in data.values():
                if plot_data.annotations["Activity"].data.empty:
                    UserInformation.inform(
                        f"There are no annotations in the plot {plot_name}. "
                        f"Therefore nothing is analyzed."
                    )

                # iterate over all labels in this plot
                annotations = plot_data.annotations["Activity"].data
                for i_activity, activity in annotations.iterrows():

                    # get the sensor data between start and end of the current annotation
                    activity_data = plot_data.data.iloc[activity.start : activity.end]

                    # calculate a feature for this part of the data
                    feature_string = self.calculate_feature(
                        activity_data, plot_data.sampling_rate_hz
                    )

                    # attach the result string to the annotation, such that it will automatically
                    # be shown as soon as the user moves the mouse over the annotation
                    plot_data.annotations["Activity"].data.at[i_activity, "description"] = feature_string

            UserInformation.inform("Algorithm executed. "
                                   "Move the mouse over a label to see the result in a pop-up.")

        @staticmethod
        def calculate_features(sensor_data: pd.DataFrame, sampling_rate_hz: float) -> str:
            #######################################################################
            ###                        README                                   ###
            ###      Here you can calculate features for example like this:     ###
            ###      feature = my_algorithm(sensor_data, sampling_rate_hz)      ###
            #######################################################################
            feature = 42
            return f"The calculated feature for this label is: {feature}."

.. admonition:: Using your algorithm in the GUI
   :class: tip

    As a last step, you need to pass the algorithm (and optionally other plugins) to the start_gui
    function, see :ref:`Pass algorithm to the GUI <pass algorithm>`.