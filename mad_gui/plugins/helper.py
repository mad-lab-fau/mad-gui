from mad_gui.plugins.base import BasePlugin
from typing import List, Type, TypeVar

T = TypeVar("T", bound=BasePlugin)


def filter_plugins(plugin_list: List[Type[BasePlugin]], baseclass: Type[T]) -> List[Type[T]]:
    return [b for b in plugin_list if issubclass(b, baseclass)]
