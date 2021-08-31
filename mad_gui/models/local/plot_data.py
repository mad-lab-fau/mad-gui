from __future__ import annotations

import pandas as pd
from mad_gui.utils.model_base import BaseStateModel, Property

from typing import Dict, List, Optional


class AnnotationData(BaseStateModel):
    data = Property(pd.DataFrame(), dtype=pd.DataFrame)

    def to_df(self):
        return self.data


class PlotData(BaseStateModel):
    # we need to initialize this with `None` for sphinx
    data: pd.DataFrame = None
    annotations: Dict = None
    sampling_rate_hz: float = None

    def to_dict(self):
        return {
            "data": self.data,
            "annotations": {k: v.to_df() for k, v in self.annotations.items()},
            "sampling_rate_hz": self.sampling_rate_hz,
        }

    def from_dict(self, plot_data: Dict, selections: Optional[List] = None) -> PlotData:
        selections = selections or ["sensor"]
        self.annotations = dict()
        for selection in selections:
            if selection == "sensor":
                self.data = plot_data["data"]
                self.sampling_rate_hz = plot_data["sampling_rate_hz"]
            elif "annotations" in plot_data.keys():
                self._add_label(plot_data, selection)
        return self

    def _add_label(self, plot_data: Dict, label: str):
        annotation = AnnotationData()
        if label in plot_data["annotations"].keys():
            # only in this case the plot_data object is aware of this kind of label
            annotation.data = plot_data["annotations"][label]
        self.annotations[label] = annotation
