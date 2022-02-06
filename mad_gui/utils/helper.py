import os
import tempfile
import warnings
from datetime import datetime, timedelta
from pathlib import Path

from PySide2.QtCore import QObject, Signal, Slot

from typing import Callable, Optional


def set_and_bind_property(slot: Slot, model_class: QObject, property_name: str, initial_set: bool = True):
    if initial_set:
        value = getattr(model_class, property_name)
        slot(value)
    get_property_signal(model_class, property_name).connect(slot)


def set_and_bidirectional_bind(
    slot: Slot,
    signal: Signal,
    model_class: QObject,
    property_name: str,
    initial_set: bool = True,
    transformer: Optional[Callable] = None,
) -> Callable:
    set_and_bind_property(slot, model_class, property_name, initial_set)
    if transformer is not None:
        func = lambda *x: setattr(model_class, property_name, transformer(*x))  # noqa
        # noqa because otherwise we need nested methodes and that's also not so nice...
    else:
        func = lambda x: setattr(model_class, property_name, x)  # noqa
    signal.connect(func)
    return lambda: signal.disconnect(func)


def get_property_signal(model_class: QObject, property_name: str) -> Signal:
    return getattr(model_class, signal_attribute_name(property_name))


def signal_attribute_name(property_name):
    """ Return a magic key for the attribute storing the signal name. """
    return f"{property_name}_changed"


def value_attribute_name(property_name):
    """ Return a magic key for the attribute storing the property value. """
    return f"_{property_name}_prop_value_"


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """

    try:
        base_path, relative_path = _get_resource_path(relative_path)
    except (IndexError, FileNotFoundError):
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def _get_resource_path(relative_path):

    paths = sorted(Path(tempfile.gettempdir()).iterdir(), key=os.path.getctime)[::-1]
    mei_paths = [p for p in paths if "_MEI" in p.name]
    time_now = datetime.today()
    newest_mei = mei_paths[0]
    date_newest_mei = datetime.fromtimestamp(os.stat(newest_mei).st_ctime)
    if (time_now - date_newest_mei) > timedelta(seconds=60):
        raise FileNotFoundError("Did not find a current _MEI folder in tmp.")
    base_path = newest_mei
    relative_path = str.replace(relative_path, ".ui", ".py")
    relative_path = str.replace(relative_path, "qt_designer", f"qt_designer{os.sep}build")
    warnings.warn(
        f"Found a _MEI folder in {tempfile.gettempdir()}, which has bee created <1 minute ago."
        f" Therefore, I assume this is called from a standalone executable."
        f" For this reason, I'm changing the resource path, from mad_gui/qt_designer/*.ui to"
        f" mad_gui/qt_designer/build/*.py"
    )

    return base_path, relative_path
