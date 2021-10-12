.. sectnum::

.. _troubleshooting:

***************
Troubleshooting
***************

.. note::
   If this troubleshooting guide does not help you to solve the problem, click `here <https://github.com/mad-lab-fau/mad-gui/issues/new?assignees=&labels=&template=bug_report.md&title=%5BBUG%5D>`_ to report a bug, click `here <https://github.com/mad-lab-fau/mad-gui/issues/new?assignees=&labels=&template=feature_request.md&title=%5BFEATURE%5D+implement+the+possibility+of+...>`_ to open a feature request, or send us an `e-mail <mailto:malte.ollenschlaeger@fau.de>`_.


Using the GUI
#############

GUI crashes when opening a video
********************************
Probably your machine is missing some codecs, which are necessary to open the video in the specific format.
In case your computer runs windows, we recommend to download and install the codes from `K-Lite Codec Pack <https://www.codecguide.com/download_k-lite_codec_pack_standard.htm>`_.

MaD GUI is not aware of descriptions for the class
**************************************************
Developers can assign a set of descriptions to a label class, as described :ref:`here <custom labels>`.
Apparently, the class that you tried to edit does not have any descriptions assigned to it.
To solve the problem, add the attribute `description` to the class in the code / talk to your developer.

Video and data not synchronized
*******************************
When loading a video, the GUI searches for an excel file that has the word `sync` in it and ends with `.xlsx` in the same folder, where the video is located.
In case it does not find such a file, you have two options:

   - work with video and data without synchronization -> you have to shift sensor data and video separately
   - use the GUI's synchronization mode to synchronize video and data

Loader provided labels that were not understood
***********************************************

This means, that the GUI does not know anything about the kind of labels the loader wants to plot.
You can read something about how to fix it in the Development section below.


.. _troubleshooting development:

Development
###########

The GUI does not start because of SystemError
*********************************************
In case you get the error `SystemError: <built-in function loadUiType> returned a result with an error set`, please
go to your Run/Debug Configurations -> Edit Configurations as shown in
`this image <_static/images/troubleshooting/edit_configurations.png>`_.

Then make sure the Box `Run with Python Console` is deactivated, as shown in
`this image <_static/images/troubleshooting/edit_configurations_02.png>`_

The GUI does not start because of TypeError
*******************************************

If you get an error like this, see the next section.

.. code-block:: console

    ... loadUiType(...)
    TypeError: cannot unpack non-iterable NoneType object


PySide2-uic not found
*********************

.. note::
    So far, this problem is only known for Windows.

.. code-block:: console

    "...mad_gui/components/dialogs/....py", line .., in <module>
    FileNotFoundError: Probably python did not find pyside2-uic

Apparently python can't find pyside2-uic, this can be solved like this.

- In your terminal / command line interface activate the environment you want to use (e.g. `conda activate mad_gui`)
- Find out, where the python installation is by using `where python` (Windows) or `which python` (Unix)
- That folder should also keep a folder `Scripts`, go there and copy `pyside2-uic` from there to the parent folder, where also python is
- Try again

Then copy pyside2-uic from the folder `Scripts` to the location where also your python executable is (should be the
parent directory).


The plugin I created does not show up in the GUI
************************************************
Please make sure that your plugin inherits from one of `BaseImporter`, `BaseAlgorithm`, or `BaseExporter`, as we
describe it in our section `Readme: Developing Plugins <https://mad-gui.readthedocs.io/en/latest/README.html#developing-plugins>`_.
Additionally, you should make sure to pass your plugin to the `start_gui` function, which is also described in the part
of `Readme: Developing Plugins <https://mad-gui.readthedocs.io/en/latest/README.html#developing-plugins>`_:

.. code-block:: python

    from mad_gui import start_gui
    from my_file imoprt MyPlugin

    start_gui(plugins=[MyPlugin]) # don't miss out the brackets, `Plugins` must be an iterable!


qt.qpa.plugin Error
*******************

.. code-block:: console

    qt.qpa.plugin: Could not load the Qt platform plugin "windows" in "" even though it was found.
 
So far, developers of MaD GUI only had problems that could be solved by adding a new system variable
`QT_QPA_PLATFORM_PLUGIN_PATH` with the value `.../Lib/site-packages/PySide2/plugins/platform` (replace the three dots to
match the path to your python instalation, e.g. C:/Users/name/anaconda3/env/mad_gui` ` to your machine. In case you are using Windows, you can find more about setting system variables `here <https://superuser.com/questions/949560/how-do-i-set-system-environment-variables-in-windows-10>`_.

In case that does not work, please see `this stackoverflow post <https://stackoverflow.com/questions/41994485/how-to-fix-could-not-find-or-load-the-qt-platform-plugin-windows-while-using-m>`_, in which you'll find a ton of possible reasons and fixes. However, please be keep in mind that the MaD GUI uses `PySide2` and not `PyQt4` or something, which is mentioned in some answers. You might therefore need to replace something from the answers to make it suit to your problem.

.. _pip stuck:

`pip install .` stuck at `Processing`
*************************************
Try to use `pip install git+https://github.com/mad-lab-fau/mad-gui.git`

Dependencies
************

In our gitlab-CI there is a dependency issue with prospector that boils down to an issue with astroid.
Therefore we manually install astroid 2.5.1 in the CI.
If you experience problems on your local machine you might consider doing this as well.


Loader provided annotations for sensors that have no plot
*********************************************************

Apparently you tried to plot annotations for a sensor, which is not in the keys of `MainWindow.sensor_plots`.
To fix that, make sure that your loaded returns a plot for this sensor.
See our section about :ref:`custom labels` for more information.

Loader provided annotations that were not understood
****************************************************

You need to pass labels with the attribute `name` equal to the ones stated in the error message to our `start_gui`
function. Read more about creating labels in our section about :ref:`custom labels`.

