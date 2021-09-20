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





## Contents of this readme
- [What is it?](#what-is-it)
- [How do I use it (videos)](#how-do-i-use-it-videos)
- [How do I get the GUI to work on my machine?](#how-do-i-get-the-gui-to-work-on-my-machine)
- [How can I test the GUI using your example data on my computer?](#how-can-i-test-the-gui-using-your-example-data-on-my-computer)
- [Can I use it with data of my specific system or a specific algorithm?](#can-i-use-it-with-data-of-my-specific-system-or-a-specific-algorithm)
- [Can I change something at the core of the GUI?](#can-i-change-something-at-the-core-of-the-gui)


##  What is it?
The MaD GUI is a framework for processing time series data.
Its use-cases include visualization, annotation (manual or automated), and algorithmic processing of visualized data and annotations.

## How do I use it?
### Videos
By clicking on the images below, you will be redirected to YouTube. In case you want to follow along on your own machine, check out the section [How do I get the GUI to work on my machine?](#how-do-i-get-the-gui-to-work-on-my-machine) first.

[<img src="./docs/_static/images/video_thumbnails/loading_and_navigating.png" width="200px">](https://www.youtube.com/watch?v=akxcuFOesC8 "MaD GUI - Loading data and navigating in the plot")
[<img src="./docs/_static/images/video_thumbnails/annotations.png" width="200px">](https://www.youtube.com/watch?v=VWQKYRRRGVA "MaD GUI - Labelling data manually or using an algorithm")
[<img src="./docs/_static/images/video_thumbnails/sync.png" width="200px">](https://www.youtube.com/watch?v=-GI5agFOPRM "MaD GUI - Synchronize video and sensor data")

### Shortcuts
Please watch the videos linked above, if you want to learn more about the different actions.

| Shortcut                     | Mode          | Action |
|------------------------------|---------------|-------|
| `a`, `e`, `r`, `s`, `Esc`    | all           | Switch between modes *Add label*, *Edit label*, *Remove label*, *Synchronize data*|
| `Space`                      | Add label     | Can be used instead of `Left Mouse Click` |
| `1`, `2`, `3`,... `TAB`      | Add label     | Navigate in the pop-up window |
| `Shift` + `Left Mouse Click` | Add label     | Start a new label directly when setting the end of a label |
| `Ctrl` + `Left Mouse Click`  | Add label     | Add a single event |

## How do I get the GUI to work on my machine?
Below, we present two options how to obtain and run the GUI.
However, this will only enable you to look at our example data.
You want to load data of a specific format/system or want to use a specific algorithm? 
In this case please refer to [Can I use it with data of my specific system or a specific algorithm?](#can-i-use-it-with-data-of-my-specific-system-or-a-specific-algorithm)

## How can I test the GUI using your example data on my computer?

First, you need to download the example data.
Right click on [this link](https://github.com/mad-lab-fau/mad-gui/raw/main/example_data/sensor_data.csv), select `Save link as...` and save it - you have to change the file ending from \*.txt to \*.csv before saving.
If you also want to check out synchronization with a video file, click on [this link](https://github.com/mad-lab-fau/mad-gui/releases/download/v0.2.0-alpha.1/video.mp4) and save it on your machine. Next, use one of the following two options (for testing it on Windows, we recommend Option A).

### Option A: Standalone executable

| Operating system       | What to do                                        |
|------------------------|---------------------------------------------------|
| Windows                | - Download our exemplary executable: [Windows (64 bit)](https://github.com/mad-lab-fau/mad-gui/releases/download/v0.2.0-alpha.1/mad_gui.exe). <br /> - Double click the downloaded file <br /> Note: If prompted with a dialog `Windows protected your PC`, click `More info` and then select `Run anyway` |
| Ubuntu                 | - Download our exemplary executable: [Ubuntu (64 bit)](https://github.com/mad-lab-fau/mad-gui/releases/download/v0.2.0-alpha.5/mad_gui_ubuntu.exe) <br /> - In your terminal: `chmod +x ./mad_gui_ubuntu.exe` and then `./mad_gui_ubuntu.exe` 
| other                  | [Contact us](mailto:malte.ollenschlaeger@fau.de)  

Start the program and then you can open the previously downloaded example data as shown in [How do I use it (videos)?](#how-do-i-use-it-videos)

### Option B: Using the python package

Info: We recommend to use `pip install mad_gui` in a [clean python virtual environment](https://docs.python.org/3/library/venv.html#creating-virtual-environments) / [conda environment](https://docs.python.org/3/library/venv.html#creating-virtual-environments).

```
pip install mad_gui
python -m mad_gui.start_gui
```

Alternatively, within a python script use our [start_gui](https://mad-gui.readthedocs.io/en/latest/modules/generated/mad_gui/mad_gui.start_gui.html#mad_gui.start_gui) function: 

```
from mad_gui import start_gui
start_gui()
```

Now you can open the previously downloaded example data as shown in [How do I use it (videos)?](#how-do-i-use-it-videos)

## Can I use it with data of my specific system or a specific algorithm?
Yes, however it will need someone who is familiar with python to perform the steps described in [Customization](https://mad-gui.readthedocs.io/en/latest/customization.html).
You do not have experience with python but still want to load data from a specific system? [Contact us!](mailto:malte.ollenschlaeger@fau.de)

Developers can get basic information about the project setup in our [Developer Guidelines](https://mad-gui.readthedocs.io/en/latest/developer_guidelines.html).
However, if you only want to extend the GUI with your custom plugins, e.g. for loading data of a specific system,
or adding an algorithm, the necessary information can be found in our documentation regarding [Customization](https://mad-gui.readthedocs.io/en/latest/customization.html).

## Can I change something at the core of the GUI?
Sure, for more information, please take a look at our [Contribution Guidelines](https://mad-gui.readthedocs.io/en/latest/contribution_guidelines.html#contribution-guidelines).
