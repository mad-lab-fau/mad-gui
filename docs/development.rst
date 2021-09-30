.. sectnum::

.. _customization:

***********
Development
***********

.. note::
   In case you experience issues, please try to find a solution in :ref:`Troubleshooting for Developers <troubleshooting development>`.

Adapting the GUI
****************

.. _other systems:

You can create plugins for the GUI, such as

   - :ref:`Importer: Load and display data of a specific system <implement importer>`
   - :ref:`Algorithm: Calculate features for existing annotations or create new annotations <implement algorithm>`
   - :ref:`Exporter: Export displayed annotations <implement exporter>`

**If you want to use the specific plugin or class in the GUI, you have to pass it to our `start_gui` function**:

.. code-block:: python

    from mad_gui import start_gui

    start_gui(plugins=[MyFirstPlugin, MySecondPlugin]
              labels=[MyCustomLabel, MyOtherCustomLabel])

You can execute the above code as a script as described in our section :ref:`Prepare Development <adding a script for execution>`.

Furthermore, as shown below on this page, you have the possibility to create your own :ref:`labels <custom labels>`,
adapt the GUI's :ref:`theme <theme>` or :ref:`constants <setting constants>`


.. _custom labels:

Custom labels
*************
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

.. _theme:

Theme
*****

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

Constants
*********

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
     # when adding an event the user will be prompted to select one of these two strings as a
     # `description` for the event
     EVENTS = ["important event", "other type of important event"]

     # Set the width of IMU plot to this, when hitting the play button for the video.
     PLOT_WIDTH_PLAYING_VIDEO = 20  # in seconds

     # If plotting large datasets, this speeds up plotting, however might result in inaccurate
     # representation of the data
     AUTO_DOWNSAMPLE = True

   start_gui(
    settings=MySettings,
   )


Send a message to the user
**************************

If - at any point - you want to send a message to the user of the GUI, you create a message box with an OK button like
this:

.. code-block:: python

   from mad_gui.user_information import UserInformation
   UserInformation.inform_user("Your message")
   yes_no = UserInformation().ask_user("Yes or No?") # will return from PySide2.QtWidgets.QMessageBox.Yes
                                                     # or from PySide2.QtWidgets.QMessageBox.No