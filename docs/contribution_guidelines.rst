.. sectnum::

.. _contribution guidelines:

***********************
Contribution Guidelines
***********************

.. warning::
   Usually you should not need this chapter. Please check :ref:`Development <customization>` to see whether you can accomplish what
   you need before using these contribution guidelines.

.. _preparing an environment:

Before you start working, you will have to create a virtual environment and install our GUI.
For more information on this, see our section :ref:`Prepare development <developer guidelines>`.


Design
######
You can change the color scheme by passing a `theme` when starting the GUI.
Please find more detailed information about how to inject such a plugin in our :ref:`API reference, section "2. Adding your plugins" <other systems>`.

In case this is not enough and you want to change something more specific, you can achieve this using the `*.ui` files in
`mad_gui/qt_designer/ <https://github.com/mad-lab-fau/mad-gui/tree/main/mad_gui/qt_designer>`_.
You can for example use the QtDesigner for it, which you should find in your PySide 2 installation
(in Windows OS located at `...anaconda3/envs/mad_gui/Lib/site-packages/PySide2/designer.exe`)
When adding / changing image buttons, be sure to do this using `window_buttons.qrc`, which afterwards needs to be transformed to a `.py` file e.g. using

.. code-block:: python

    pyrcc5 -o window_buttons_rc.py window_buttons.qrc

Note, that you have to change the import on the resulting `.py` file from PyQt5 to PySide2.


Contributing
############

Creating a merge request
************************
Before you start, create a new branch based on development named like this `<feature-you-want-to-implement>`, to describe roughly what you would like to fix or add.
Afterwards, create a merge request.
Be sure to have a `WIP:` at the very beginning of its name.
Source branch is the branch you just created and target branch is `development`.
Do not choose an assignee yet.

In the description, write shortly what you are going to fix or add, then make commits (see next section).

Pushing code
************
Before pushing code, be sure to call `doit` from commandline within the project folder.
This will automatically trigger the following commands, which you can also call separately:

.. code-block:: python

    doit format_check
    doit lint
    doit test
    doit docs

* `doit format_check` checks if the code format is OK with respect to line length and so on. You can handle errors from format check by calling `doit format` or using `black` in your IDE.

* `doit lint` takes care for code style, you'll have to fix those messages manually in your code.

* `doit test` runs all tests in the `.tests` folder to make sure everything is still working as expected. (in future we will expand testing such that most of the implemented code is tested and such that new code fragments will have to be tested by the person who implements it before the merge request will be merged).

* `doit docs` builds the documentation from the comments in the code. You can view the created documentation in docs/_build/html/index.html.

In case you are experiencing problems with the task `doit lint`, you may want to install a newer version of astrod:

.. code-block:: python

    pip install git+https://github.com/PyCQA/astroid.git@astroid-2.5.1

Request to merge code
*********************
When you think your implementation is done, remove `WIP:` from the merge request's name (e.g. by marking it as ready).
Then, assign a reviewer to the merge request, this person will have to review your code, see [2.4 Reviewing Code](#reviewing-code)
After the review has been completed, the reviewer will merge your changes into development.


Reviewing code
##############
Make sure, code is readable and understandable for others. This includes for example things like these:

* does the method (variable) do (keep) what its name suggest it does?
* is the maximum level of indentation three or four, so one can easily choose a level of abstraction at which to read the code and easily understand the code?
* is code duplication avoided?
* is the method free of side-effects?
* does the documentation render properly?
* ...

Maybe have a look at `Uncle Bob Clean Code <https://www.youtube.com/watch?v=7EmboKQH8lM>`_, which is an entertaining way of learning.
In case you prefer to read, take a look at `PEP <https://www.python.org/dev/peps/pep-0008/>`_.



