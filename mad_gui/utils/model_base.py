import pandas as pd
from PySide2.QtCore import Property as QtProperty
from PySide2.QtCore import QObject, Signal, Slot
from typing_extensions import Literal

from mad_gui.utils import helper
from typing import Any, Callable, Optional, Type, TypeVar


# TODO: Handle nullable values
class PropertyMeta(type(QObject)):
    def __new__(cls, name, bases, attrs):
        for key, attr in list(attrs.items()):
            if not isinstance(attr, Property):
                continue
            initial_value = attr.initial_value
            dtype = attr.dtype
            if not dtype:
                dtype = type(initial_value)
            notifier = Signal(dtype)
            attrs[key] = PropertyImpl(initial_value, name=key, dtype=dtype, notify=notifier)
            attrs[helper.signal_attribute_name(key)] = notifier
        return super().__new__(cls, name, bases, attrs)


T = TypeVar("T")


class Property:
    """Property definition.

    This property will be patched by the PropertyMeta metaclass into a PropertyImpl type.
    """

    def __init__(self, initial_value: Optional[T] = None, dtype: Optional[Type[T]] = None):
        self.initial_value = initial_value
        self.dtype = dtype

    def __get__(self, instance, owner) -> T:
        """Fake getter for typechecker"""
        return self.initial_value

    def __set__(self, instance, value: T):
        """Fake setter for typechecker"""
        pass  # noqa


class PropertyImpl(QtProperty):
    """ Actual property implementation using a signal to notify any change. """

    def __init__(self, initial_value, name, dtype=None, notify=None):
        super().__init__(dtype, self._getter, self._setter, notify=notify)
        self.initial_value = initial_value
        self.dtype = dtype
        self.name = name

    def _getter(self, inst):
        return getattr(inst, helper.value_attribute_name(self.name), self.initial_value)

    def _setter(self, inst, value):
        last_value = self._getter(inst)
        if not self._is_equal(last_value, value):
            setattr(inst, helper.value_attribute_name(self.name), value)
            notifier_signal = getattr(inst, helper.signal_attribute_name(self.name))
            notifier_signal.emit(value)

    def _is_equal(self, old, new):
        if self.dtype == pd.DataFrame:
            assert isinstance(old, pd.DataFrame)
            return old.equals(new)
        return old == new


class BaseStateModel(QObject, metaclass=PropertyMeta):
    def bind(self, slot: Slot, property_name: str, initial_set: bool = True):
        helper.set_and_bind_property(slot, self, property_name, initial_set)

    def bind_bidirectional(
        self,
        slot: Slot,
        signal: Signal,
        property_name: str,
        initial_set: bool = True,
        transformer: Optional[Callable] = None,
    ) -> Callable:
        return helper.set_and_bidirectional_bind(slot, signal, self, property_name, initial_set, transformer)

    def bind_property_bidirectional(
        self,
        model: "BaseStateModel",
        target_property_name: str,
        property_name: str,
        initial: Optional[Literal["get", "set"]] = None,
    ):
        if initial == "get":
            target_value = getattr(model, target_property_name)
            setattr(self, property_name, target_value)
        elif initial == "set":
            value = getattr(self, property_name)
            setattr(model, property_name, value)
        return helper.set_and_bidirectional_bind(
            lambda x: setattr(model, target_property_name, x),
            getattr(model, helper.signal_attribute_name(target_property_name)),
            self,
            property_name,
            initial_set=False,
            transformer=None,
        )

    def set(self, property_name: str, value: Any):
        setattr(self, property_name, value)
        return self
