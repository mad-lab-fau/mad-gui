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

        data = {"Pocket IMU": pd.read_csv(file)[["acc_x", "acc_y", "acc_z", "gyr_x", "gyr_y", "gyr_z"]]}
        sampling_rate = 1 / df["time"].diff().mean()
        return data, sampling_rate

    def load_annotations(self, file_path: Union[Path, str]) -> Dict[str, pd.DataFrame]:
        return


class ExampleAlgorithm(BaseAlgorithm):
    @classmethod
    def name(cls):
        return "Find Resting Phases (example MaD GUI)"

    def process_data(self, data: Dict[str, PlotData]) -> Dict[str, PlotData]:
        for sensor_plot in data.values():
            sensor_plot.annotations["Activity"].data = self.get_annotations(sensor_plot.data)

    @staticmethod
    def get_annotations(data: pd.DataFrame):
        acc = data[["acc_x", "acc_y", "acc_z"]]
        motion = acc.diff().apply(np.linalg.norm, axis=1)

        # sampling rate was 102.4 and we choose ~one second as window length
        window_length = 102

        standing_windows = abs(motion.rolling(window=window_length).mean()) < 0.2

        # from standing_windows we get only a single one if the complete windows is standing -> we need to transform
        # this single one to a series of window_length ones
        standing = np.zeros(shape=(1, len(acc)))
        for idx, value in standing_windows.iteritems():
            if value:
                filter_lag = window_length
                start = max(0, idx - filter_lag)
                stop = min(idx + window_length - filter_lag, len(acc))
                standing[0, start:stop] = 1

        # now we have something like [0 1 1 1 1 0], which we want to transform to start: 1, end: 4
        standing = pd.DataFrame(standing).T
        starts_stops = standing.diff()
        annotations = pd.DataFrame(columns=["start", "end"])
        for idx, value in standing.iterrows():
            if starts_stops[0].iloc[idx] == 1:
                start = idx
            if starts_stops[0].iloc[idx] == -1 or idx == len(standing):
                stop = idx
                annotations = annotations.append(pd.DataFrame(data=[[start, stop]], columns=["start", "end"]))
        annotations["description"] = "standing"
        return annotations
