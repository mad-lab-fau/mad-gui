from __future__ import annotations

import pandas as pd

from mad_gui.utils.model_base import BaseStateModel, Property
from typing import Dict, List, Optional


class AnnotationData(BaseStateModel):
    """An object that just represents a pandas.DataFrame and makes it possible to bind the dataframe to methods.

    This object is used to present starts, ends and descriptions of labels in a plot. It is used in
    :class:`mad_gui.models.local.PlotData.annotations`.

    Attributes
    ----------
    data
        An object which represents a pandas.DataFrame at least with the columns `start` and `end`.
        Each row encodes one label.

    Methods
    -------
    data_changed
        A signal that is emitted as soon as data is changed. We use it internally to synchronize this object's
        data, which is stored in :class:`mad_gui.windows.MainWindow.global_data.plot_data`, with the regarding sensor
        plot, which can be found in :class:`mad_gui.windows.MainWindow.sensor_plots`.

    to_df
        Utility method to return self.data as a pandas.DataFrame.

    Examples
    --------
    >>> plot_data = gui.global_data.plot_data
    >>> for plot, data in plot_data.items():
    ...      print(f"Sensor {plot}'s annotations are:")
    ...      for label_class, annotation_df in data.annotations.items():
    ...           print(f"Labels of class {label_class}: ")
    ...           print(annotation_df.data)
    ...
    Sensor Pocket IMU's annotations are:
    Labels of class Base Label:
    identifier  start   end description details
             0   1687  2238    (sleep,)    None
    """

    data = Property(pd.DataFrame(), dtype=pd.DataFrame)

    def to_df(self):
        return self.data


class PlotData(BaseStateModel):
    """An object, which keeps the plotted data and annotations of a single plot.

    Attributes
    ----------
    data
        A pandas.DataFrame, where each column is one channel of plotted data.

    sampling_rate_hz
        The sampling rate with which the data was recorded.

    annotations
        A dictionary, where the keys are the label names (as named in the label's
        :meth:`~mad_gui.plot_tools.labels.BaseRegionLabel.name` attribute). The values are instances of
        :class:`~mad_gui.models.local.AnnotationData`.

    additional_data
        Keeps things that belongs to the plotted data but should not be plotted. Here you can find everything that was
        returned from your loader for one sensor, where the key is not `sensor_data` or `sampling_rate_hz`, see
        :class:`mad_gui.plugins.BaseImporter`.
    """

    # we need to initialize this with `None` for sphinx
    data: pd.DataFrame = None
    sampling_rate_hz: float = None
    annotations: Dict = None
    additional_data: Dict = None

    def to_dict(self):
        return {
            "sensor_data": self.data,
            "annotations": {k: v.to_df() for k, v in self.annotations.items() if k != "events"},
            "events": self.annotations["events"].to_df(),
            "sampling_rate_hz": self.sampling_rate_hz,
        }

    def from_dict(self, plot_data: Dict, selections: Optional[List] = None) -> PlotData:
        selections = selections or plot_data.keys() - {"sampling_rate_hz"}
        self.annotations = {}
        for selection in selections:
            if selection == "sensor_data":
                try:
                    self.data = plot_data["sensor_data"]
                    self.sampling_rate_hz = plot_data["sampling_rate_hz"]
                except KeyError as k:
                    raise KeyError(
                        "Please provide sensor data and a sampling rate for each sensor in your loader's "
                        "`load_sensor_data` method. For docstring on that method see https://mad-gui.readthe"
                        "docs.io/en/latest/modules/generated/plugins/mad_gui.plugins.BaseImporter.html#mad_g"
                        "ui.plugins.BaseImporter.load_sensor_data"
                    ) from k
                continue
            if selection == "annotations":
                self._add_annotations(plot_data)
                continue
            # when loading data from pickle, we do not get `annotations` but directly the label names as selections
            if not self._add_label(plot_data, selection):
                if not self.additional_data:
                    self.additional_data = {}
                self.additional_data[selection] = plot_data[selection]
        self.annotations["events"] = AnnotationData()
        self._add_events(getattr(plot_data, "events", None))
        return self

    def _add_annotations(self, plot_data: Dict):
        if not plot_data.get("annotations", None):
            return
        for label in plot_data["annotations"].keys():
            self._add_label(plot_data, label)

    def _add_events(self, events: pd.DataFrame):
        if not events:
            return
        global_labels = [label for label in self.parent().global_data.labels if label.name in self.annotations]
        for _, event in events.iterrows():
            for label in global_labels:
                if event.min_height == label.min_height and event.max_height == label.max_height:
                    self.annotations["events"].data = self.annotations["events"].data.append(event)

    def _add_label(self, plot_data: Dict, label: str):
        if not plot_data.get("annotations", None):
            return False
        annotation = AnnotationData()
        if label in plot_data["annotations"].keys():
            # only in this case the plot_data object is aware of this kind of label
            annotation.data = plot_data["annotations"][label]
            self.annotations[label] = annotation
            return True
        return False
