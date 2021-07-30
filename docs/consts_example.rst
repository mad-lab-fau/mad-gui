.. _configs:

Setting Constants
=================

.. note::
   If you want to understand the context of this file, make sure to at least quickly take a look at our :ref:`developer guidelines`, specifically the
   section :ref:`other systems`.

This file lists all the possibilities you have to adapt the GUI.
If you want to use them, create a file named `consts_<your system name>.py` in `mad_gui.config`.
To adapt the behavior of the GUI, copy the parts you need from this document.
Afterwards, go to the bottom of the file `mad_gui/main.py` and change the line

.. code-block:: python

   form = MainWindow()

to

.. code-block:: python

    form = MainWindow(consts_file="mad_gui.config.consts_<your system name>")

.. _axes to plot:

Axes to plot
------------
Those are the axes which are plotted by default after loading data.
However, you can change that at runtime by right-clicking on a graph and then go to the submenu "Select Axes".
Note that the axis names need to fit the axis names that are in the loaded data.

.. code-block:: python

   AXES_TO_PLOT = [
       "acc_pa",
       "gyr_ml"
   ]

.. _consts activity labels:

Activity labels
---------------
After adding an activity, there will be a pop-up window, which gives you the possiblity to assign one of the following
activity types to it. Furthermore, you can select those labels, for which you additionally want to provide details in 
a separate pop-up window.

.. code-block:: python

   ACTIVITIES = [
       "sitting",
       "moving"
   ]
   ASK_FOR_LABEL_DETAILS = True  # or False
   DETAILED_ACTIVITIES = [
       "moving",
   ]
   DETAILS = ["walk", "run"]  # options for details, if user selected activity_type2 before

.. _consts-stride-labels:

Stride labels
-------------
Currently, there are two kinds of stride labels implemented. `SegmentedStrideLabels` just have a start and end, `StrideLabels` additionally have a `tc` event (terminal contact). If you want the start and end of stride to snap to a minimum in gyroscope medio-lateral data, set the bool constant. The range in which the GUI searches for a minimum can be selected by the third constant (in seconds).

.. code-block:: python

   from mad_gui.plot_tools import StrideLabel, SegmentedStrideLabel
   STRIDE_LABEL_CLASS = <StrideLabel or SegmentedStrideLabel>
   STRIDE_SNAP_TO_MIN = <True or False>
   SNAP_RANGE_S = 0.1


Label ranges
------------
This sets the vertical region, in which the stride labels are. In this example they occupy middle 50% of the plot.
The space above is used for activity labels / annotations.

.. code-block:: python

   MAX_HEIGHT_STRIDE_LABELS = 0.75
   MIN_HEIGHT_STRIDE_LABELS = 0.25


Standard plot width
-------------------
Set the width of IMU plot to this, when hitting the play button for the video.

.. code-block:: python

   PLOT_WIDTH_PLAYING_VIDEO = 20  # in seconds

