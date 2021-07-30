from __future__ import annotations

import pandas as pd

from mad_gui.plot_tools.base_label import BaseRegionLabel
from mad_gui.utils.model_base import BaseStateModel, Property
from typing import TYPE_CHECKING, Dict, List, Optional, Type

if TYPE_CHECKING:
    from mad_gui.plugins.base import BaseImporter, BasePlugin  # pylint: disable=ungrouped-imports


class AnnotationData(BaseStateModel):
    data = Property(pd.DataFrame(), dtype=pd.DataFrame)


class PlotData(BaseStateModel):
    data: pd.DataFrame
    # stride_annotations = Property(pd.DataFrame(), dtype=pd.DataFrame)
    # activity_annotations = Property(pd.DataFrame(), dtype=pd.DataFrame)
    # irgendwo: PlotData.annotations[] = AnnotationData(...)
    # --> binds auf instanz v. annotation data
    annotations: Dict
    sampling_rate_hz: float

    def to_dict(self):
        return {
            "data": self.data,
            "stride_annotations": self.stride_annotations,
            "activity_annotations": self.activity_annotations,
            "sampling_rate_hz": self.sampling_rate_hz,
        }

    def from_dict(self, plot_data: Dict, selections: Optional[List] = None) -> PlotData:
        selections = selections or ["sensor"]
        self.annotations = dict()
        for selection in selections:
            if selection == "sensor":
                self.data = plot_data["data"]
                self.sampling_rate_hz = plot_data["sampling_rate_hz"]
            else:
                self._add_label(plot_data, selection)
        return self

    def _add_label(self, plot_data: PlotData, label: str):
        annotation = AnnotationData()
        if label in plot_data.keys():
            annotation.data = plot_data[label]
        self.annotations[label] = annotation


class GlobalData(BaseStateModel):
    data_file = Property("", dtype=str)
    video_file = Property("", dtype=str)
    sync_file = Property("", dtype=str)
    annotation_file = Property("", dtype=str)
    base_dir = Property("", dtype=str)

    plot_data: Dict[str, PlotData] = Property({}, dtype=dict)

    plugins: List[Type[BasePlugin]]
    labels: List[Type[BaseRegionLabel]]
    active_loader: BaseImporter
