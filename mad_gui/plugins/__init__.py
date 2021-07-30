# pylint: skip-file
"""The :py:mod:`mad_gui.plugins` keeps files that tell the GUI how to interact with data from different sources.

If data of a specific system should be used within our GUI, a file in this directory needs to implement the
functionalities given by :py:mod:`mad_gui.plugins.base`, see classes below.
"""

from mad_gui.plugins.base import BaseExporter, BaseImporter

__all__ = [
    "BaseImporter",
    "BaseExporter",
]
