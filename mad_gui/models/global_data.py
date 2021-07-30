from __future__ import annotations

import pandas as pd

from mad_gui.utils.model_base import BaseStateModel, Property
from typing import TYPE_CHECKING, Dict, List, Optional, Type

if TYPE_CHECKING:
    from mad_gui.plugins.base import BaseImporter, BasePlugin  # pylint: disable=ungrouped-imports


class PlotData(BaseStateModel):
    data: pd.DataFrame
    stride_annotations = Property(pd.DataFrame(), dtype=pd.DataFrame)
    activity_annotations = Property(pd.DataFrame(), dtype=pd.DataFrame)
    sampling_rate_hz: float

    def to_dict(self):
        return {
            "data": self.data,
            "stride_annotations": self.stride_annotations,
            "activity_annotations": self.activity_annotations,
            "sampling_rate_hz": self.sampling_rate_hz,
        }

    def from_dict(self, plot_data: Dict, selection: Optional[List] = None) -> PlotData:
        selection = selection or ["sensor", "strides", "activities"]
        if "sensor" in selection:
            self.data = plot_data["data"]
        if "strides" in selection:
            self.stride_annotations = plot_data.get("stride_annotations", pd.DataFrame())
        if "activities" in selection:
            self.activity_annotations = plot_data.get("activity_annotations", pd.DataFrame())
        self.sampling_rate_hz = plot_data["sampling_rate_hz"]
        return self


class GlobalData(BaseStateModel):
    data_file = Property("", dtype=str)
    video_file = Property("", dtype=str)
    sync_file = Property("", dtype=str)
    annotation_file = Property("", dtype=str)
    base_dir = Property("", dtype=str)

    plot_data: Dict[str, PlotData] = Property({}, dtype=dict)

    plugins: List[Type[BasePlugin]]
    active_loader: BaseImporter
