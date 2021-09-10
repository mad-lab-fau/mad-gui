.. _troubleshooting:

***************
Troubleshooting
***************

.. note::
   If this troubleshooting guide does not help you to solve the problem, send us an `e-mail <mailto:mad-digait@fau.de>`_.


Using the GUI
#############

GUI crashes when opening a video
********************************
Probably your machine is missing some codecs, which are necessary to open the video in the specific format.
In case your computer runs windows, we recommend to download and install the codes from `K-Lite Codec Pack <https://www.codecguide.com/download_k-lite_codec_pack_standard.htm>`_.

MaD GUI is not aware of descriptions for the class
**************************************************
Developers can assign a set of descriptions to a label class, as described :ref:`here <creating custom labels>`.
Apparently, the class that you tried to edit does not have any descriptions assigned to it.
To solve the problem, add the attribute `description` to the class in the code / talk to your developer.

Video and data not synchronized
*******************************
When loading a video, the GUI searches for an excel file that has the word `sync` in it and ends with `.xlsx` in the same folder, where the video is located.
In case it does not find such a file, you have two options:

   - work with video and data without synchronization -> you have to shift sensor data and video separately
   - use the GUI's synchronization mode to synchronize video and data

Loader provided annotations that were not understood
****************************************************

This means, that the GUI does not know anything about the kind of annotations the loader wants to plot.
You can read something about how to fix it in the Development section below.


Development
###########

qt.qpa.plugin Error
*******************
If using Visual Studio, you might get this error on starting the GUI:

.. code-block:: python

    qt.qpa.plugin: Could not load the Qt platform plugin "windows" in "" even though it was found.
    
You can fix it as described in `this stackoverflow answer<https://stackoverflow.com/a/42231526>`_.

.. _pip stuck:

`pip install .` stuck at `Processing`
*************************************

Deactivate the experimental new installer: `poetry config experimental.new-installer false`

Dependencies
************

In our gitlab-CI there is a dependency issue with prospector that boils down to an issue with astroid.
Therefore we manually install astroid 2.5.1 in the CI.
If you experience problems on your local machine you might consider doing this as well.

Fail to load UI
***************

If you get an error like this, see the next section.

.. code-block:: python

    ... loadUiType(...)
    TypeError: cannot unpack non-iterable NoneType object


PySide2-uic not found
*********************

.. note::
    So far, this problem is only known for Windows.

.. code-block:: python

    "...mad_gui\components\dialogs\....py", line .., in <module>
    FileNotFoundError: Probably python did not find pyside2-uic

Probably python can't find pyside2-uic. Look for a folder called `Scripts` in your python env.
To find the location of your python env, go to the command line, activate the environment and then type:

Operating system | command
-----------------|--------
Windows          | where python

Then copy pyside2-uic from the folder `Scripts` to the location where also your python executable is (should be the
parent directory).

Loader provided annotations for sensors that have no plot
*********************************************************

Apparently you tried to plot annotations for a sensor, which is not in the keys of `MainWindow.sensor_plots`.
To fix that, make sure that your loaded returns a plot for this sensor.
See our section about `Customization <https://mad-gui.readthedocs.io/en/latest/customization.html#implement-an-importer>`_
for more information.



Loader provided annotations that were not understood
****************************************************

You need to pass labels with the attribute `name` equal to the ones stated in the error message to our `start_gui`
function. Read more about creating labels in our section about :ref:`Customization <customization>`.
