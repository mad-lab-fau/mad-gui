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
In case it does not find such a file, you receive the message `Could not find a synchronization file for video and data`.
You have two options:

   - work with video and data without synchronization -> you have to shift sensor data and video separately
   - use the GUI's synchronization mode to synchronize video and data, as described in our `How To` (see top of the page).


Development
###########

Dependencies
************

In our gitlab-CI there is a dependency issue with prospector that boils down to an issue with astroid.
Therefore we manually install astroid 2.5.1 in the CI.
If you experience problems on your local machine you might consider doing this as well.

Testing fails in PyCharm command line but works otherwise
*********************************************************
For some reason, some test execute properly if you click the "play" button right next to it.
However, if you call `doit test` within the command line in PyCharm it may fail because of

```
PluginSelectorWindow, BasePluginSelectorWindow = loadUiType(str(UI_PATH / "export.ui"))
E   TypeError: cannot unpack non-iterable NoneType object
```

In this case, simply switch to your computer's command line and call `doit test` from there.
