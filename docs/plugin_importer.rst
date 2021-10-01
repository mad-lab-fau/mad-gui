.. sectnum::

.. _implement importer:

********
Importer
********

Overview
########

This enables our GUI to load and display your specific type of data, as shown in the video form 0:10 to 0:20.
Please additionally take a look at `this GIF <_static/gifs/importer.gif>`_, which shows you how your plugin gets into the GUI.

.. raw:: html

   <p style="text-align:center;">
   <iframe width="560" height="315" align="middle" src="https://www.youtube.com/embed/akxcuFOesC8?start=9" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
   </p>


Create a file that will include your custom importer
####################################################

.. image:: _static/images/development/importer_create_file.png
    :alt: Creating a file for the plugin
    :height: 250

Develop your custom importer in that file
#########################################

.. note::

   If the user selects your CustomImporter, selects a file and then presses `start_processing`, the GUI will pass the
   selected file to your `CustomImporter.load_sensor_data` (argument `file_path`), as shown in `this GIF <_static/gifs/importer.gif>`_.

Use this code snippet and

- optional: set the file type that the importer can load, e.g. "*.csv"
- set the importer's name as return value of the regarding method
- make sure the variable `sensor_data` in `load_sensor_data` keeps a dataframe
- fill the variabel `sampling_rate_hz` in `load_sensor_data`



.. code-block:: python

   """These are the contents of custom_importer.py, which holds my first importer."""

   from typing import Dict
   import pandas as pd
   from mad_gui import start_gui, BaseImporter

   loadable_file_type = "*.*"

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
         ###    it to a pandas dataframe (columns are sensor channels,  ###
         ###    ass for example "acc_x". Assign it to sensor_data.      ###
         ###                                                            ###
         ### b) load the sampling rate (int or float)                   ###
         ##################################################################
         sensor_data =
         sampling_rate_hz =

         # CAUTION: if you only want to have one plot you do not need to
         # change the following lines!
         # If you want several plots, just add another sensor like "IMU foot"
         # to the `data` dictionary.
         data = {
         "IMU Hip": {
             "sensor_data": sensor_data,
             "sampling_rate_hz": sampling_rate_hz,
             }
         }

         return data

Pass the developed importer class to `start_gui`
################################################

.. code-block:: python

   from mad_gui import start_gui
   from custom_importer import CustomImporter

   start_gui(plugins=[CustomImporter])

.. image:: _static/images/development/importer_pass_to_gui.png
    :alt: Making the plugin available in the GUI

After you have performed these steps, you can select the importer in the GUI by pressing `Load Data`
and then selecting it in the dropdown on the upper left in the pop-up window.
From user perspective it should work as we have described in our
`exemplary video about loading data <https://youtu.be/akxcuFOesC8?t=10>`_.

If the user presses `Start processing`, the path to the selected file will be passed to the selected loader's
`load_sensor_data` method, as shown in `the GIF <_static/gifs/importer.gif>`_.
After returning the dictionary from this method to the GUI, the GUI will plot the data.

.. note::
    In case loading your file does not work, we recommend to set breakpoints into your loader and check, whether
    everything does what you expect it to do. Also you might want to look at our section about
    :ref:`Troubleshooting development <troubleshooting development>` or at
    `load_sensor_data's documentation <https://mad-gui.readthedocs.io/en/latest/modules/generated/plugins/mad_gui.plugins.BaseImporter.html#mad_gui.plugins.BaseImporter.load_sensor_data>`_.
