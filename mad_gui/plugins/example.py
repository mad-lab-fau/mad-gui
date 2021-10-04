import os
from pathlib import Path

import numpy as np
import pandas as pd
from PySide2.QtWidgets import QFileDialog

from mad_gui.components.dialogs import UserInformation
from mad_gui.models import GlobalData
from mad_gui.models.local import PlotData
from mad_gui.plugins.base import BaseAlgorithm, BaseExporter, BaseImporter
from typing import Dict, Tuple, Union


class ExampleImporter(BaseImporter):
    """Classes based on this one enable the GUI to handle data from different systems."""

    file_type = "*.csv"

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


class StationaryMomentsDetector(BaseAlgorithm):
    @classmethod
    def name(cls):
        return "Find Resting Phases (MaD GUI example)"

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


class EnergyCalculator(BaseAlgorithm):
    @classmethod
    def name(cls):
        return "Mean energy of acceleration (MaD GUI example)"

    def process_data(self, plot_data: Dict[str, PlotData]):
        for sensor_plot in plot_data.values():
            for i_activity, activity in sensor_plot.annotations["Activity"].data.iterrows():
                description = sensor_plot.annotations["Activity"].data.at[i_activity, "description"]
                sensor_plot.annotations["Activity"].data.at[i_activity, "description"] = (
                    str(description)
                    + " ("
                    + self.calculate_features(sensor_plot.data.iloc[activity.start : activity.end])
                    + ")"
                )

    @staticmethod
    def calculate_features(sensor_data: pd.DataFrame) -> str:
        signal = sensor_data[["acc_x", "acc_y", "acc_z"]]
        energy = np.sqrt((signal ** 2).sum(axis=1).mean())
        return f"mean acceleration = {energy:.2f}"


class ExampleExporter(BaseExporter):
    @classmethod
    def name(cls):
        return "Export annotations to csv (MaD GUI example)"

    def process_data(self, global_data: GlobalData):
        directory = QFileDialog().getExistingDirectory(
            None, "Save .csv results to this folder", str(Path(global_data.data_file).parent)
        )
        for plot_name, plot_data in global_data.plot_data.items():
            for label_name, annotations in plot_data.annotations.items():
                if len(annotations.data) == 0:
                    continue
                annotations.data.to_csv(
                    directory + os.sep + plot_name.replace(" ", "_") + "_" + label_name.replace(" ", "_") + ".csv"
                )

        UserInformation.inform(f"The results were saved to {directory}.")
