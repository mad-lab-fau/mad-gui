from __future__ import annotations

import pandas as pd
from mad_gui.plot_tools.labels import BaseRegionLabel
from mad_gui.utils.model_base import BaseStateModel, Property

from typing import TYPE_CHECKING, Dict, List, Optional, Type

if TYPE_CHECKING:
    from mad_gui.plugins.base import BaseImporter, BasePlugin  # pylint: disable=ungrouped-imports


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

    def _add_label(self, plot_data: PlotData, label: str):
        annotation = AnnotationData()
        if label in plot_data["annotations"].keys():
            # only in this case the plot_data object is aware of this kind of label
            annotation.data = plot_data["annotations"][label]
        self.annotations[label] = annotation


class GlobalData(BaseStateModel):
    """A single object per MaD GUI instance that keeps global data.

    Parameters
    ----------
    active_loader
        One of the loaders passed to start_gui, which have inherited from :class:`~mad_gui.plugins.BaseImporter`. It
        can be selected by the user via the dropdown menu in the
        :class:`~mad_gui.components.dialogs.plugin_selection.LoadDataDialog`.
    data_file
        File of the currently data that is selected by the user in the
        :class:`~mad_gui.components.dialogs.plugin_selection.LoadDataDialog`.
    sync_file
        A file that keeps synchronization between video and sensor data. The GUI automatically searches for a file in
        the same folder as the video_file and if it finds a file, that has `*sync*.xlsx` in it assumes, this keeps
        the video synchronization.
    video_file
        File which contains the video to be displayed in the
        :class:`~mad_gui.components.dialogs.plugin_selection.LoadDataDialog`.
    plot_data
        The keys are the names of the plots and the values are :class:`~mad_gui.models.PlotData` objects.
    plugins
        All plugins, that the GUI is aware of. The GUI is aware of all plugins that were passed to it via
        :meth:`~mad_gui.start_gui`.
    """

    data_file = Property("", dtype=str)
    video_file = Property("", dtype=str)
    sync_file = Property("", dtype=str)
    annotation_file = Property("", dtype=str)
    base_dir = Property("", dtype=str)

    plot_data: Dict[str, PlotData] = Property({}, dtype=dict)

    # we need to initialize this with `None` for sphinx
    plugins: List[Type[BasePlugin]] = None
    labels: List[Type[BaseRegionLabel]] = None
    active_loader: BaseImporter = None
