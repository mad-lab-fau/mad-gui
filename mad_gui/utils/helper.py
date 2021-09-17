import os

from PySide2.QtCore import QObject, Signal, Slot

import platform
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
        if platform.system() == "Windows":
            paths = os.environ.get("PATH").split(";")
        elif platform.system() in ["Linux", "Darwin"]:
            paths = os.listdir("/tmp/")
        base_path = [p for p in paths if "_MEI" in p][0]
        relative_path = str.replace(relative_path, ".ui", ".py")
        relative_path = str.replace(relative_path, "qt_designer", f"qt_designer{os.sep}build")
    except IndexError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
