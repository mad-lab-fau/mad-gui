.. sectnum::

.. _executable:

**********
Executable
**********

You may wish to create a standalone executable of your version of MaD GUI.
This might for example be useful, if someone wants to use it who does not want to or cannot install anything on their machine.
Please note, that the executable will only work on the operating system it is built on.
If you need it to work on Windows and MacOS for exameple, then you also need to built it once on windows and once on MacOS.

We use pyinstaller to create the executable.
The steps that need to be performed are described below.
If you need more information about pyinstaller, please refer to the `official documentation <https://pyinstaller.readthedocs.io/en/stable/index.html>`_.


.. _retrieve files:

Retrieve necessary files
########################

First, you need to get some files to the location where your script is, which starts the MaD GUI.
Therefore, you need the following files. 
Right click and save as... for the following files to the location, where your script is, which starts the GUI:

* `dodo.py <https://github.com/mad-lab-fau/mad-gui/raw/main/dodo.py?raw=true>`_
* `mad-runnier.ico <https://github.com/mad-lab-fau/mad-gui/blob/main/mad-runner.ico?raw=true>`_
* `splash.jpg <https://github.com/mad-lab-fau/mad-gui/blob/main/docs/_static/images/splash.jpg?raw=true>`_
* `pyinstaller.spec <https://github.com/mad-lab-fau/mad-gui/raw/main/pyinstaller.spec>`_

Configure requirements / dependencies
#####################################

List all requirements in a file, e.g. requirements.txt (inlcuding mad_gui).
Those requirements must include everything that is needed by your plugins.

Create a virtual environment
############################

Install a clean python version.
We recommend that you do not use anaconda since this might lead to issues with packaging.
Also we recommend not to have python in your PATH variable to avoid confusions.
Next, we are going to set up an environment just for packaging.
Therefore, open a terminal and navigate to your script which starts mad_gui in terminal, then:

Windows
*******

1. ``<path to your fresh py installation>\\python -m venv .venv``
2. ``.venv\\Scripts\\activate``
3. ``.venv\\Scripts\\python.exe -m pip install --upgrade pip``
4. ``.venv\\Scripts\\pip install . pillow doit pyinstaller``

Unix
****

1. ``<path to your fresh py installation>\python -m venv .venv``
2. ``source .venv/bin/activate``
3. ``.venv/bin/python -m pip install --upgrade pip``
4. ``.venv/bin/pip install . pillow doit pyinstaller``


Transform UI files
##################

Now we can prepare the build - we need to transform some files using the `dodo.py` from :ref:`the first step in this manual <retrieve files>` in the directory where the .venv as well as your script to start the GUI are.
It will transform some .ui files to .py files and copies them into `.venv/Lib/site-packages/mad_gui/qt_designer/build` (Unix: `.venv/lib/python3.7/site-packages/...`)

``doit prepare_build``

Configure and use pyinstaller
#############################

Next open the file `pyinstaller.spec`. 
In the line `a = Analysis(['start.py'])` change `start.py` to the python script that starts your version of the GUI.
In case your algorithms need some files, for example .csv files make sure to add them to the argument `datas` a few lines below.
Also, you might need to add some `hiddenimports` further below in case pyinstaller does not find all the dependencies - you will find that out when you can not start the executable later.

``pyinstaller pyinstaller.spec``

Finally, you can find the standalone executable in the dist folder.
