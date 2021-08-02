# MaD GUI 
***M***achine Learning 
***a***nd 
***D***ata Analytics 
***G***raphical 
***U***ser 
***I***nterface

![Test and Lint](https://github.com/mad-lab-fau/mad-gui/workflows/Test%20and%20Lint/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/mad-gui/badge/?version=latest)](https://mad-gui.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

##  What is it?
The MaD GUI is a framework for processing time series data.
Its use-cases include visualization, annotation (manual or automated), and algorithmic processing of visualized data and annotations.

## How do I get the GUI?
Below, we provide two ways of how to get the GUI. 
In case one of these fails for you, please refer to our troubleshooting guide [Link coming soon].
You want to load data of a specific format or want to use a specific algorithm? 
In this case please refer to ["Can I use it with data of my specific system or a specific algorithm?"](#can-i-use-it-with-data-of-my-specific-system-or-a-specific-algorithm).

### Standalone executable
The GUI can be packed into stand-alone executables, such that is not necessary for you to install anything on your machine.

- Windows users: download our exemplary executable here [Coming soon]
- Other operating systems: [Contact us](mailto:mad-digait@fau.de).

### Using the python package
```
pip install git+https://github.com/mad-lab-fau/mad-gui.git
```

From your command line either simply start the GUI or pass additional arguments:
```
python -m mad_gui.start_gui
python -m mad_gui.starg_gui --base_dir C:/my_data
```

Alternatively, within a python script use our [start_gui](https://github.com/mad-lab-fau/mad-gui/blob/2857ccc20766ea32f847271771b52c97e2682b79/mad_gui/start_gui.py#L26) 
function and hand it over the path where your data resides, `<data_path>` like `"C:/data"` or `"/home/data/"`: 
```
from mad_gui import start_gui
start_gui(<data_path>)
```

## How do I interact with the GUI?
<soon there will be one or more videos here, which show(s) how the GUI works>

- loading data / video / annotations
- adding annotations via an algorithm
- synchronize video and data
- export data / apply other algorithms and export results

## Can I use it with data of my specific system or a specific algorithm?
Yes, however it will need someone who is familiar with python.
Developers can learn more about how to create plugins for our GUI here [Link coming soon].
You do not have experience with python but still want to load data from a specific system? [Contact us!](mailto:mad-digait@fau.de)

## Can I change something at the core of the GUI?
Sure, we try to document the most important parts of the GUI to make adaption as easy as possible.
Take a look at the developer guidelines for more information [Link coming soon].