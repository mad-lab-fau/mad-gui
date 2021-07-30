import pandas as pd

from mad_gui.plugins.base import BaseImporter
from typing import Dict, Tuple


class ExampleImporter(BaseImporter):
    """Classes based on this one enable the GUI to handle data from different systems."""

    @classmethod
    def name(cls) -> str:
        return "Example Importer"

    def load_sensor_data(self, file: str) -> Tuple[Dict, float]:
        df = pd.read_csv(file)

        data = {"Acceleration": pd.read_csv(file)[["acc_x", "acc_y", "acc_z"]]}
        sampling_rate = 1 / df["time"].diff().mean()
        return data, sampling_rate
