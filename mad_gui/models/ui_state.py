from typing_extensions import Literal

from mad_gui.utils.model_base import BaseStateModel, Property

MODES = Literal["investigate", "sync", "add", "modify", "remove"]


class UiState(BaseStateModel):
    menu_collapsed = Property(True)


class PlotState(BaseStateModel):
    x_range = Property((0, 1))
    y_range = Property((0, 1))
    x_range_max = Property((0, 1))
    mode: MODES = Property("investigate", dtype=str)
