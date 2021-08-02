.. _contribution guidelines:

***********************
Contribution Guidelines
***********************


1. Configurating PyCharm
########################
Open the downloaded/cloned repository as a PyCharm project.
Then, add the file `mad_gui/start_gui` to PyCharm's `Run / Debug configurations`.
If you need help with this, please take a look at our :ref:`API Reference, section "2. Adding a script for execution" <adding a script for execution>`.


2 Design
########
You can change the color scheme by passing a `theme` when starting the GUI.
In case this is not enough and you want to change something more specific, you can achieve this using the *.ui files in
`mad_gui/qt_designer/ <https://github.com/mad-lab-fau/mad-gui/tree/main/mad_gui/qt_designer>`_.
You can for example use the QtDesigner for it, which you should find in your PySide 2 installation
(in Windows OS located at `...anaconda3/envs/mad_gui/Lib/site-packages/PySide2/designer.exe`)
When adding / changing image buttons, be sure to do this using `window_buttons.qrc`, which afterwards needs to be transformed to a `.py` file e.g. using

.. code-block:: python

    pyrcc5 -o window_buttons_rc.py window_buttons.qrc

Note, that you have to change the import on the resulting `.py` file from PyQt5 to PySide2.



