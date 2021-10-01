# MaD GUI 
**M**achine Learning 
**a**nd 
**D**ata Analytics 
**G**raphical 
**U**ser 
**I**nterface

[![Test and Lint](https://github.com/mad-lab-fau/mad-gui/workflows/Test%20and%20Lint/badge.svg)](https://github.com/mad-lab-fau/mad-gui/actions/workflows/test_and_lint.yml)
[![CodeFactor](https://www.codefactor.io/repository/github/mad-lab-fau/mad-gui/badge/main)](https://www.codefactor.io/repository/github/mad-lab-fau/mad-gui/overview/main)
[![Documentation Status](https://readthedocs.org/projects/mad-gui/badge/?version=latest)](https://mad-gui.readthedocs.io/en/latest/?badge=latest)


[![PyPI version shields.io](https://img.shields.io/pypi/v/mad-gui)](https://pypi.org/project/mad-gui/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mad-gui)

![GitHub all releases](https://img.shields.io/github/downloads/mad-lab-fau/mad-gui/total?style=social)
[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCaLchy07OciePfHL9j-8u8A?style=social)](https://m.youtube.com/channel/UCaLchy07OciePfHL9j-8u8A/videos)

<div align="center">
  
:warning: ![WARNING](https://img.shields.io/badge/-WARNING-yellow) :warning: <br />
This is still an early version. Things might not work as expected. <br />
Experiencing issues? [Report a bug here!](https://github.com/mad-lab-fau/mad-gui/issues/new?assignees=&labels=&template=bug_report.md&title=%5BBUG%5D)

  
</div>

## Contents of this readme

Here you can find some general information to find out whether the our packages suits your needs:
- [What is it?](#what-is-it)
- [How does the user interface work?](#how-does-the-user-interface-work)
- [How do I get the GUI to work on my machine?](#how-do-i-get-the-gui-to-work-on-my-machine)
- [How can I test the GUI using your example data on my computer?](#how-can-i-test-the-gui-using-your-example-data-on-my-computer)
- [Can the GUI load and display data of my specific system?](#can-the-gui-load-and-display-data-of-my-specific-system)
- [Can the GUI use my own algorithm?](#can-the-gui-use-my-own-algorithm)
- [Can I change something at the core of the GUI?](#can-i-change-something-at-the-core-of-the-gui)

Here you can find information about development:
- [Developing plugins](#developing-plugins)
- [Communicating with the user](#communicating-with-the-user)
- [Adjusting Constants](#adjusting-constants)
- [Changing the theme](#change-the-theme)

##  What is it?
The MaD GUI is a framework for processing time series data.
Its use-cases include visualization, annotation (manual or automated), and algorithmic processing of visualized data and annotations.

## How does the user interface work?

### Videos

By clicking on the images below, you will be redirected to YouTube. In case you want to follow along on your own machine, check out the section [How do I get the GUI to work on my machine?](#how-do-i-get-the-gui-to-work-on-my-machine) first.

[<img src="./docs/_static/images/video_thumbnails/loading_and_navigating.png" width="200px">](https://www.youtube.com/watch?v=akxcuFOesC8 "MaD GUI - Loading data and navigating in the plot")
[<img src="./docs/_static/images/video_thumbnails/annotations.png" width="200px">](https://www.youtube.com/watch?v=VWQKYRRRGVA "MaD GUI - Labelling data manually or using an algorithm")
[<img src="./docs/_static/images/video_thumbnails/sync.png" width="200px">](https://www.youtube.com/watch?v=-GI5agFOPRM "MaD GUI - Synchronize video and sensor data")


### Shortcuts
Please watch the videos linked above, if you want to learn more about the different actions.

| Shortcut <img width=50/>                     | Mode <img width=50/>          | Action |
|------------------------------|---------------|-------|
| `a`, `e`, `r`, `s`, `Esc`    | all           | Switch between modes *Add label*, *Edit label*, *Remove label*, *Synchronize data*|
| `Left Mouse Click`           | Add label     | Set start/end of a label|
| `Space`                      | Add label     | Can be used instead of `Left Mouse Click` |
| `1`, `2`, `3`,... `TAB`      | Add label     | Navigate in the pop-up window |
| `Shift` + `Left Mouse Click` | Add label     | Start a new label directly when setting the end of a label |
| `Ctrl` + `Left Mouse Click`  | Add label     | Add a single event |

## How do I get the GUI to work on my machine?
In the next section, we present two options how to obtain and run the GUI.
However, this will only enable you to look at our example data.
You want to load data of a specific format/system or want to use a specific algorithm? 
In this case please refer to [Can I use it with data of my specific system or a specific algorithm?](#can-i-use-it-with-data-of-my-specific-system-or-a-specific-algorithm)

### How can I test the GUI using your example data on my computer?

First, you need to download the example data.
Click on [this link](https://github.com/mad-lab-fau/mad-gui/raw/main/example_data/sensor_data.zip), and extract the file to your computer.
If you also want to check out synchronization with a video file, click on [this link](https://github.com/mad-lab-fau/mad-gui/releases/download/v0.2.0-alpha.1/video.mp4) and save it on your machine. Next, use one of the following two options (for testing it on Windows, we recommend Option A).

#### End-user: Standalone executable

When downloading the files below, your browser may warn you that this is a potentially dangerous file.
You will only be able to use our GUI by selecting "Keep anyway / download anyway / ...".
In the case of Microsoft Edge, this possiblity is hidden, but you can select it after downloading as explained [here](https://docs.microsoft.com/en-us/deployedge/microsoft-edge-security-downloads-interruptions#user-experience-for-downloads-lacking-gestures).

| Operating system <img width=200/>      | File to download <img width=200/>| What to do                                        |
|------------------------|------------------|---------------------------------------------------|
| Windows                | [Windows (64 bit)](https://github.com/mad-lab-fau/mad-gui/releases/download/v0.2.0-alpha.1/mad_gui)       | Download the file on the left. Then open the ownloaded file. <br /> <br />*Note: If prompted with a dialog `Windows protected your PC`, click `More info` and then select `Run anyway`* |
| Ubuntu                 | [Ubuntu (64 bit)](https://github.com/mad-lab-fau/mad-gui/releases/download/v0.2.0-alpha.5/mad_gui_ubuntu) | Download the file on the left. Then, in your terminal, navigate to the file loaction and then: `chmod +x ./mad_gui_ubuntu` and then `./mad_gui_ubuntu` <br /> <br />*Note: you might need to install some additional packages. You can use [this script](https://raw.githubusercontent.com/mad-lab-fau/mad-gui/main/unix_dependencies.sh) to do so. Just right click the link, save it on your machine and execute it.*|
| Mac OS                 | [Mac OS (64 bit)](https://github.com/mad-lab-fau/mad-gui/releases/download/v0.2.0-alpha.5/mad_gui_mac.zip) | Download the file on the left and extract it. Then, in your [terminal](https://support.apple.com/en-lk/guide/terminal/apd5265185d-f365-44cb-8b09-71a064a42125/mac), navigate to the location where you extracted "mad_gui_mac.app" to. Then type `chmod +x ./mad_gui_mac.app` and then `./mad_gui_mac.app` <br /><br /> *Note: If your Mac does not allow you to open this file, perform the actions for "If you want to open an app that hasn’t been notarized or is from an unidentified developer" on the [Apple Support Page](https://support.apple.com/en-us/HT202491). Afterwards, try `./mad_gui_mac.exe` again in your terminal.*|
| other                  | Supplied upon request |[Contact us](mailto:malte.ollenschlaeger@fau.de)  

Start the program, and then you can open the previously downloaded example data as shown in [How do I use it (videos)?](#how-do-i-use-it-videos)

#### Developers: Using the python package

Info: We recommend to use `pip install mad_gui` in a [clean python virtual environment](https://docs.python.org/3/library/venv.html#creating-virtual-environments) / [conda environment](https://docs.python.org/3/library/venv.html#creating-virtual-environments). 
This way you do NOT need to clone this github repository.
Afterwards, you can simply start our GUI from your terminal:

```
pip install mad_gui
mad-gui
```

Alternatively, within a python script use our [start_gui](https://mad-gui.readthedocs.io/en/latest/modules/generated/mad_gui/mad_gui.start_gui.html#mad_gui.start_gui) function: 

```
from mad_gui import start_gui
start_gui()
```

Now you can open the previously downloaded example data as shown in [How do I use it (videos)?](#how-do-i-use-it-videos)

## Can the GUI load and display data of my specific system?
Yes, however it will need someone who is familiar with Python. For more information, please refer to [Developing Plugins](#developing-plugins).
You do not have experience with python but still want to load data from a specific system? [Contact us!](mailto:malte.ollenschlaeger@fau.de)

## Can the GUI use my own algorithm?
Yes, however it will need someone who is familiar with Python. For more information, please refer to [Developing Plugins](#developing-plugins).
You do not have experience with python but still want to load data from a specific system? [Contact us!](mailto:malte.ollenschlaeger@fau.de)

## Can I change something at the core of the GUI?
Yes, for more information, please [get in touch](mailto:malte.ollenschlaeger@fau.de).

## Developing Plugins
The MaD GUI package is a framework, which can be extended with different kinds of plugins and labels.
The user can access your plugins within the GUI using dropdowns, after clicking "Load data" or "Use algorithm". 
**However, this is only possible if your plugin was passed to the GUI at startup**:

```python
from mad_gui import start_gui
from my_importer import MyImporter
from my_algorithm import MyAlgorithm
from my_labels import MyFirstLabel, MySecondLabel

# only passing plugins
start_gui(plugins=[MyImporter, MyAlgorithm])

# passing plugins and labels
start_gui(plugis=[MyImporter], labels=[MyFirstLabel, MySecondLabel])

```

In the sections in the following list we describe how you can develop your own plugins and labels, which must inherit one of our 
[base plugins](https://mad-gui.readthedocs.io/en/latest/modules/plugins.html#plugins) or 
[BaseRegionLabel](https://mad-gui.readthedocs.io/en/latest/modules/generated/plot_tools/mad_gui.plot_tools.labels.BaseRegionLabel.html#mad_gui.plot_tools.labels.BaseRegionLabel).
**Each of these sections keeps working example to get you started as quick as possible**:

   - Importer: [Load and display data of a specific system](https://mad-gui.readthedocs.io/en/latest/plugin_importer.html#importer)
   - Algorithm: [Create annotations for plotted data](https://mad-gui.readthedocs.io/en/latest/plugin_algorithm.html#algorithm)
   - Algorithm: [Calculate features for existing annotations](https://mad-gui.readthedocs.io/en/latest/plugin_algorithm.html#algorithm)
   - Exporter: [Export displayed annotations](https://mad-gui.readthedocs.io/en/latest/plugin_exporter.html)
   - Labels: [Create one or several custom label classes](file:///D:/mad-gui/docs/_build/html/labels.html#labels)
   - For supplementary basic information please refer to [Preparation](https://mad-gui.readthedocs.io/en/latest/developer_guidelines.html).

## Communicating with the user

If - at any point - you want to send a message to the user of the GUI, you create a message box with an OK button like
this:

```python
from mad_gui.components.dialogs.user_information import UserInformation

UserInformation.inform_user("Your message")

# will return PySide2.QtWidgets.QMessageBox.Yes or PySide2.QtWidgets.QMessageBox.No
yes_no = UserInformation().ask_user("Yes or No?") 
```

## Changing the theme

You can easily change the two dominating colors by passing your own theme to the GUI.

```python
   from mad_gui import start_gui
   from mad_gui.config import BaseTheme
   from PySide2.QtGui import QColor

   class MyTheme(BaseTheme):
      COLOR_DARK = QColor(0, 255, 100)
      COLOR_LIGHT = QColor(255, 255, 255)

   start_gui(
    theme=MyTheme,
   )
```

## Adjusting Constants

You can create your own settings by creating a class, which inherits from our [BaseSettings](https://github.com/mad-lab-fau/mad-gui/blob/main/mad_gui/config/settings.py#L1)>`_.
The following example makes use of the BaseSettings and simply overrides some properties:

```python
from mad_gui.config import BaseSettings
from mad_gui import start_gui
   
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

```
