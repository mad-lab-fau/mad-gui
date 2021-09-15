from pathlib import Path

import numpy as np
import pandas as pd

from mad_gui.models.local import PlotData
from mad_gui.plugins.base import BaseAlgorithm, BaseImporter
from typing import Dict, Tuple, Union


class ExampleImporter(BaseImporter):
    """Classes based on this one enable the GUI to handle data from different systems."""

    @classmethod
    def name(cls) -> str:
        return "Example Importer"

    def load_sensor_data(self, file: str) -> Tuple[Dict, float]:
        df = pd.read_csv(file)

        data = {
            "Pocket IMU": {
                "sensor_data": pd.read_csv(file)[["acc_x", "acc_y", "acc_z", "gyr_x", "gyr_y", "gyr_z"]],
                "sampling_rate_hz": 1 / df["time"].diff().mean(),
            }
        }
        return data

    def load_annotations(self, file_path: Union[Path, str]) -> Dict[str, pd.DataFrame]:
        return


class ExampleAlgorithm(BaseAlgorithm):
    @classmethod
    def name(cls):
        return "Find Resting Phases (example MaD GUI)"

    def process_data(self, plot_data: Dict[str, PlotData]):
        for sensor_plot in plot_data.values():
            sensor_plot.annotations["Activity"].data = self.get_annotations(sensor_plot.data)

    @staticmethod
    def _get_standing_windows(data: pd.DataFrame, window_length: int):
        diff = data.diff().apply(np.linalg.norm, axis=1)

        standing_windows = abs(diff.rolling(window=window_length).mean()) < 0.2

        # from standing_windows we get only a single one if the complete windows is standing -> we need to transform
        # this single one to a series of window_length ones
        standing = np.zeros(shape=(1, len(data)))
        for idx, value in standing_windows.iteritems():
            if value:
                filter_lag = window_length
                start = max(0, idx - filter_lag)
                stop = min(idx + window_length - filter_lag, len(data))
                standing[0, start:stop] = 1
        return standing

    @staticmethod
    def _binary_to_df(array: np.ndarray):
        # now we have something like [0 1 1 1 1 0], which we want to transform to start: 1, end: 4
        df = pd.DataFrame(array).T
        starts_stops = df.diff()
        annotations = pd.DataFrame(columns=["start", "end"])
        start = stop = None
        for idx in df.index:
            if starts_stops[0].iloc[idx] == 1:
                start = idx
            if start and (starts_stops[0].iloc[idx] == -1 or idx == len(df)):
                stop = idx
            if start and stop:
                annotations = annotations.append(pd.DataFrame(data=[[start, stop]], columns=["start", "end"]))
                start = None
                stop = None
        return annotations

    def get_annotations(self, data: pd.DataFrame):
        acc = data[["acc_x", "acc_y", "acc_z"]]

        # sampling rate was 102.4 and we choose ~one second as window length
        flags_standing = self._get_standing_windows(acc, window_length=102)
        annotations = self._binary_to_df(flags_standing)
        annotations["description"] = "standing"
        return annotations
