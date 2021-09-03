# MaD GUI 
**M**achine Learning 
**a**nd 
**D**ata Analytics 
**G**raphical 
**U**ser 
**I**nterface

[![Test and Lint](https://github.com/mad-lab-fau/mad-gui/workflows/Test%20and%20Lint/badge.svg)](https://github.com/mad-lab-fau/mad-gui/actions/workflows/test_and_lint.yml)
[![Documentation Status](https://readthedocs.org/projects/mad-gui/badge/?version=latest)](https://mad-gui.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# DISCLAIMER
The current version is not stable and might crash unexpectedly!

##  What is it?
The MaD GUI is a framework for processing time series data.
Its use-cases include visualization, annotation (manual or automated), and algorithmic processing of visualized data and annotations.

## How do I use it (videos)?
By clicking on the images below, you will be redirected to YouTube. In case you want to follow along on your own machine, check out the section ["How do I get the GUI to work on my machine?](#how-do-i-get-the-gui-to-work-on-my-machine) first.

[<img src="./docs/_static/images/video_thumbnails/loading_and_navigating.png" width="300">](https://www.youtube.com/watch?v=Vq45DcQAVnQ "MaD GUI - Loading data and navigating in the plot")


- adding annotations via an algorithm
- synchronize video and data
- export data / apply other algorithms and export results

## How do I get the GUI to work on my machine?
Below, we present two options how to obtain and run the GUI.
However, this will only enable you to look at our example data.
You want to load data of a specific format/system or want to use a specific algorithm? 
In this case please refer to ["Can I use it with data of my specific system or a specific algorithm?"](#can-i-use-it-with-data-of-my-specific-system-or-a-specific-algorithm).

## How can I test the GUI using your example data on my computer?

First, you need to download the example data.
Right click on [this link](https://raw.githubusercontent.com/mad-lab-fau/mad-gui/main/example_data/smartphone/acceleration.csv), select `Save link as...` and save it as `acceleration.csv`.
If you also want to check out synchronization with a video file, then right click on [this link](https://github.com/mad-lab-fau/mad-gui/releases/download/v0.2.0-alpha.1/video.mp4) and select `Save link as...` to store it on your machine. Next, use one of the following two options (for testing it on Windows, we recommend Option A).

### Option A: Standalone executable

- Windows users: download our exemplary executable [here](https://github.com/mad-lab-fau/mad-gui/releases/download/v0.2.0-alpha.1/mad_gui.exe)
- Other operating systems: [Contact us](mailto:mad-digait@fau.de).

Start the program and then you can open the previously downloaded example data as shown in [How do I use it?](#how-do-i-use-it).

### Option B: Using the python package
```
pip install mad_gui
```
Make sure to include the underscore.
If you do not include it, you will install a different package.

Then, from your command line either simply start the GUI (first line) or pass additional arguments (second line):
```
mad-gui
python -m mad_gui.start_gui --base_dir C:/my_data
```

Alternatively, within a python script use our [start_gui](https://github.com/mad-lab-fau/mad-gui/blob/2857ccc20766ea32f847271771b52c97e2682b79/mad_gui/start_gui.py#L26) 
function and hand it over the path where your data resides, `<data_path>` like `C:/data` or `/home/data/`: 
```
from mad_gui import start_gui
start_gui(<data_path>)
```

Now you can open the previously downloaded example data as shown in [How do I use it?](#how-do-i-use-it).


## Can I use it with data of my specific system or a specific algorithm?
Yes, however it will need someone who is familiar with python to perform the steps described in [Customization](https://mad-gui.readthedocs.io/en/latest/customization.html).
You do not have experience with python but still want to load data from a specific system? [Contact us!](mailto:malte.ollenschlaeger@fau.de)

Developers can get basic information about the project setup in our [Developer Guidelines](https://mad-gui.readthedocs.io/en/latest/developer_guidelines.html).
If you want to extend the GUI with your custom plugins, e.g. for loading data of a specific system,
or adding an algorithm, the necessary information can be found in our documentation regarding [Customization](https://mad-gui.readthedocs.io/en/latest/customization.html).

## Can I change something at the core of the GUI?
Sure, for more information, please take a look at our [Contribution Guidelines](https://mad-gui.readthedocs.io/en/latest/contribution_guidelines.html#contribution-guidelines).
