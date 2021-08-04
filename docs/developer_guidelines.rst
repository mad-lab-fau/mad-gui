.. _developer guidelines:

********************
Developer Guidelines
********************

In the first four sections we give some information about the project setup.
If you are familiar with PyCharm and python virtual environments, you may directly jump to :ref:`Adapting the GUI <adapting the gui>`.

1 Installing necessary software
*******************************
Necessary software to be installed in advance:

    - `anaconda <https://www.anaconda.com/products/individual>`_
    - `PyCharm <https://www.jetbrains.com/pycharm/>`_

Anaconda will be used to create a python virtual environment into which all dependencies of the GUI are going to be installed.
This virtual environment will then be used as python interpreter in the PyCharm IDE to develop the GUI.

.. _preparing environment

2. Preparing an environment
***************************
After installing anaconda, open the Anaconda Prompt.
Then create a virtual environment in there by using the following commands:

.. code-block:: python

    conda create -n mad_gui python=3.7 --no-default-packages
    conda activate mad_gui

If the environment is activated you can see `(mad_gui)` in the commandline before your next input.

.. image:: res/images/conda_activated.png
    :width: 400
    :alt: Environment "mad_gui" activated in command prompt



3 Installing MaD GUI
********************
You have two possibilities for installing the dependencies:
using `pip <https://pip.pypa.io/en/stable/installing/>`_ or using `poetry <https://python-poetry.org>`_.
Using `pip` is easier and we suggest to use this if you want to get going quickly.
However, if using `pip` causes problems regarding dependencies, you should switch to using `poetry`.

3.1 Using pip
#############
In the anaconda command prompt type the following command. Before, make sure `mad_gui` is still activated (see :ref:`Preparing environment <preparing environment>`):

.. code-block::

    pip install mad_gui
    
Make sure to include the underscore!
Otherwise, you will be installing something else.

3.2 Using Poetry
################
Stay in the anaconda prompt and switch to the directory, where you have downloaded the repository to.
Most likely, you will need commands like these:

.. code-block::

    cd ..  # to go to a parent directory
    cd folder_name  # to enter a folder
    dir  # (Windows) to list all files/folders in the current working directory
    ls  # (Unix) to list all files/folders in the current working directory

As soon as you have navigated to the repository's folder and you can see files like `pyproject.toml`, the installation can start.
Therefore, you first need to set up poetry.
Setting up `poetry` with `conda` as the main Python version can be a little tricky.
First, make sure that you installed poetry in the `recommended way <https://python-poetry.org/docs/#installation>`_ using
the PowerShell command.

Then you have 2 options to start using poetry for this package:

1. Using a `conda env` instead of `venv`

.. code-block:: python

    # Install dependencies
    # Poetry will `detect that you are already using a conda env <https://github.com/python-poetry/poetry/pull/1432>`_ and will use it, instead of creating a new one.
    poetry install --no-root`

After running the poetry install command you should be able to use poetry without activating the conda env again.
You just have to set up your IDE to use the conda env you created (see next section).

2. Using `conda` python and a `venv`
    - This only works, if your conda **base** env has a Python version supported by the project (>= 3.7)
    - Activate the base env
    - Run `poetry install --no-root`. Poetry will create a new venv in the folder `.venv`, because it detects and handles the conda base env
      `different than other envs <https://github.com/maksbotan/poetry/blob/b1058fc2304ea3e2377af357264abd0e1a791a6a/poetry/utils/env.py#L295>`_.
    - Everything else should work like you are not using conda




.. _Configuring PyCharm:

4 Configuring PyCharm
***********************

You can either configure the python interpreter in pycharm directly while creating the project, or afterwards.
Both options are described below.

4.1 When setting up the project
###############################

Open PyCharm and create a new project.
On the left hand side, select `Pure Python`.
On the right hand side:

   1. Set the location to a path where you want to keep the project.

   2. Unfold the element `Python Interpreter`

   3. Select `Previously configured interpreter` and click on the three dots on the very right

   4. On the left hand side select `Conda Environment`

   5. On the right hand side select the environment you have created before. By default, the environment should be located in:

      5.1 Windows: C:/Users/<your user name>/anaconda3/envs/mad_gui/python

      5.2 Unix: home/<user>/anaconda3/envs/mad_gui/python

4.2 After setting up the project
################################
In your opened project, do the following steps:

   1. File -> Settings -> Project: <your project name> -> Python Interpreter

   2. Click the wheel on the top right and then `Add...`

   3. On the left hand side select `Conda Environment`

   4. On the right hand side choose the radio button `Existing environment`

   5. Select the `python` of the environment you created, by default it should be here:

      5.1 Windows: `C:/<user>/anaconda3/envs/mad_gui/python`

      5.2 Unix: `home/<user>/anaconda3/envs/mad_gui/python`

.. _adapting the gui:

5 Adapting the GUI
******************
We created the GUI in a way, that you can inject your own plugins into the GUI.
These can then for example take care for loading data of a specific format.
Furthermore, you have the possibility to inject algorithms this way.
If you want to do that, you will need our :ref:`API Reference <api reference>`.

In case you there is something that you want to change in the GUI, which is not possible using plugins,
you will need our :ref:`Contribution Guidelines <contribution guidelines>`.

6 Creating an executable
************************

You may want to ship the GUI including your plugin(s) to users, who are not familiar with python and/or do not have the possibilites to install something on their machine.
In this case, you can create an executable of the GUI as follows:

* install a clean python version (not using anaconda)
* afterwards, follow these steps in the clean python installation (not in your virutal environment mad_gui!):

.. code-block:: python

    # navigate to the repository
    cd mad_gui

    # create virutal environment
    python -m venv .venv
    # this creates the virutal environment in the folder `.venv`
    # the `doit` task `prepare_windows_build` will make use of this folder by default later in this process

    # activate the virutal environment
    .venv/Scripts/activate

    # Install project dependencies
    pip install .

    # get PyInstaller (make sure pyinstaller is NOT installed in your global python!)
    pip install pyinstaller

    # we need this to perform the following task
    pip install doit

    # we have to transform some .ui files to .py and but them into our .venv mad-gui library
    # note: if you did not name your virtual environment .venv in the second step, you can pass the name using `-v <name of venv>`
    doit prepare_windows_build

    # actually create the executable
    pyinstaller pyinstaller.spec

Afterwards, you will find the file in the `dist` folder
Sometimes pyinstaller does not find all the imports. In that case, you might need to make use of its
`hidden import <https://pyinstaller.readthedocs.io/en/stable/when-things-go-wrong.html#listing-hidden-imports>`_
option.


