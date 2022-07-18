# MaD GUI
**M**achine Learning 
**a**nd 
**D**ata Analytics 
**G**raphical 
**U**ser 
**I**nterface

[![Test and Lint](https://github.com/mad-lab-fau/mad-gui/workflows/Test%20and%20Lint/badge.svg)](https://github.com/mad-lab-fau/mad-gui/actions/workflows/test_and_lint.yml)
[![Documentation Status](https://readthedocs.org/projects/mad-gui/badge/?version=latest)](https://mad-gui.readthedocs.io/en/latest/?badge=latest)


[![PyPI version shields.io](https://img.shields.io/pypi/v/mad-gui)](https://pypi.org/project/mad-gui/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mad-gui)

![GitHub all releases](https://img.shields.io/github/downloads/mad-lab-fau/mad-gui/total?style=social)

## What is it?
The MaD GUI is a framework for processing time series data. Its use-cases include visualization, annotation (manual or automated), and algorithmic processing of visualized data and annotations. More information:

 - [Documentation](https://mad-gui.readthedocs.io/en/latest/README.html) 
 - [Github Repository](https://github.com/mad-lab-fau/mad-gui)
 - [YouTube Playlist](https://www.youtube.com/watch?v=cSFFSTUM4e0&list=PLf4GpKhBjGcswKIkNeahNt5nDxt8oXPue)

## Using our example

In a python 3.8 environment, execute the following commands or use the section [Development installation](https://github.com/mad-lab-fau/mad-gui#development-installation):
```
pip install mad_gui
mad-gui
```

This is just to get a first feeling of how the GUI looks like, you can test with our example data:
You can [download our example data](https://github.com/mad-lab-fau/mad-gui#example-data) to
test our built-in exemplary importer, exemplary algorithms and exemplary label. 
To see how to open our example data within the GUI, please refer to our section about the 
[User Interface](https://github.com/mad-lab-fau/mad-gui#user-interface).

## Using your data / algorithms

Very short, you will create and inject plugins, similar to this:

```
from mad_gui import start_gui
from my_plugin_package imoprt MyAlgorithm

start_gui(plugins=MyAlgorithm)
```

For more information on how to create your plugins, refer to [our readme](https://github.com/mad-lab-fau/mad-gui#developing-plugins) or our [more extensive documentation](https://mad-gui.readthedocs.io/en/latest/plugin_importer.html).
