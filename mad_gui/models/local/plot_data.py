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
        """Return the annotations stored in this object as :class:`pandas.DataFrame`"""
        return self.data


class PlotData(BaseStateModel):
    """An object, which keeps the plotted data and annotations of a single plot.

    Parameters
    ----------
    data
        A pandas.DataFrame, where each column is one channel of plotted data.

    sampling_rate_hz
        The sampling rate with which the data was recorded.

    annotation
        A dictionary, where the keys are the label names (as named in the label's
        :meth:`~mad_gui.plot_tools.labels.BaseRegionLabel.name` attribute). The values are instances of
        :class:`~mad_gui.models.local.AnnotationData`.

    additional_data
        Keeps things that belongs to the plotted data but should not be plotted. Here you can find everything that was
        returned from your loader for one sensor, where the key is not `sensor_data` or `sampling_rate_hz`, see
        :class:`mad_gui.plugins.BaseImporter`.
    """

    def __init__(self, data: pd.DataFrame, sampling_rate_hz: float, annotation: Dict = None, additional_data=None):
        self.data = data
        self.sampling_rate_hz = sampling_rate_hz
        self.annotations = annotation or {}
        self.additional_data = additional_data

    def to_dict(self):
        """Represent this object as a dictionary, such that it can be pickled.

        Returns
        -------
        dict
            A dictionary with the keys `sensor_data`, `annotations`, `events`, and `sampling_rate_hz`,
            where the first three are :class:`pandas.DataFrame` and the last is a float.
        """
        return {
            "sensor_data": self.data,
            "annotations": {k: v.to_df() for k, v in self.annotations.items() if k != "events"},
            "events": self.annotations["events"].to_df(),
            "sampling_rate_hz": self.sampling_rate_hz,
        }

    @classmethod
    def from_dict(cls, plot_data: Dict, selections: Optional[List] = None) -> PlotData:
        """Create an instance of this class from a dictionary.

        Parameters
        ----------
        plot_data
            A dictionary with a key `sensor_data`, which is a :class:`pandas.DataFrame`; a key `sampling_rate_hz`,
            which is a float`; optionally a key `annotations` containing a dictionary, where keys are label names (
            :attr:`mad_gui.plot_tools.labels.BaseRegionLabel.name`) and each value is a :class:`pandas.DataFrame` at
            least with the columns `start` and `end` and optional columns `description` and `identifier`.
        selections
            This is used to indicate which of the items in the passed dictionary plot_data should be plotted. We use it
            only when using the "reload displayed data" button.

        Returns
        -------
        PlotData
        """

        selections = selections or plot_data.keys() - {"sampling_rate_hz"}

        if not all(required_key in plot_data.keys() for required_key in ["sensor_data", "sampling_rate_hz"]):
            raise KeyError(
                "Your importer's `load_sensor_data` method must return a dict at least with the keys `sensor_data` "
                f"and `sampling_rate_hz`, but it has {plot_data.keys()}. For docstring on that method see https://mad-"
                "gui.readthedocs.io/en/latest/modules/generated/plugins/mad_gui.plugins.BaseImporter.html#mad_gui."
                "plugins.BaseImporter.load_sensor_data"
            )
        sensor_data = plot_data["sensor_data"]
        sampling_rate_hz = plot_data["sampling_rate_hz"]

        obj = cls(sensor_data, sampling_rate_hz)
        for selection in set(selections) - {"sensor_data", "sampling_rate_hz"}:
            if selection == "annotations":
                obj._add_annotations(plot_data)
                continue

            if not obj._add_label(plot_data, selection):
                obj._add_additional_data(obj, plot_data, selection)

        obj.annotations["events"] = AnnotationData()
        obj._add_events(getattr(plot_data, "events", None))
        return obj

    @staticmethod
    def _add_additional_data(obj, plot_data, selection):
        if not obj.additional_data:
            obj.additional_data = {}
        obj.additional_data[selection] = plot_data[selection]

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
