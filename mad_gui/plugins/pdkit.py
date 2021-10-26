from typing import Dict
import pandas as pd
from mad_gui.plugins import BaseAlgorithm
from mad_gui.components.dialogs.user_information import UserInformation
from mad_gui.models.local import PlotData
import numpy as np
from pdkit.gait_processor import GaitProcessor


class GaitDetector(BaseAlgorithm):
    @classmethod
    def name(cls) -> str:
        name = "PdKit Segmentation"
        return name

    def process_data(self, data: Dict[str, PlotData]):
        for plot_name, sensor_plot in data.items():
            # Use the currently plotted data to create annotations
            annotations = self.create_annotations(sensor_plot.data, sensor_plot.sampling_rate_hz)
            UserInformation.inform(f"Found {len(annotations)} annotations for {plot_name}.")
            sensor_plot.annotations["Activity"].data = annotations

    def create_annotations(self, sensor_data: pd.DataFrame, sampling_rate_hz: float) -> pd.DataFrame:
        """Some code that creates a pd.DataFrame with the columns `start` and `end`.

        Each row corresponds to one annotation to be plotted.
        """
        bouts = self.apply_pdkit_segmentation(sensor_data, sampling_rate_hz)
        starts = bouts["start_sample"]
        ends = bouts["end_sample"]

        annotations = pd.DataFrame(data=[starts, ends], index=['start', 'end']).T
        return annotations

    @staticmethod
    def _reformat_data(df: pd.DataFrame, sampling_rate_hz: float):
        df = df[["acc_x"]]
        df = df.join(pd.DataFrame(data=df.index / sampling_rate_hz, columns=["td"]))
        datetimes = pd.DataFrame(pd.to_datetime(df["td"], unit="s"))
        datetimes.columns = ["timestamp"]
        df = df.join(datetimes)
        df = df.set_index("timestamp")
        return df

    @staticmethod
    def _get_gaitbouts_from_clusters(
        peak_pos_samples, prominences, clusters
    ) -> pd.DataFrame:
        starts_idx = np.nonzero(clusters - np.roll(clusters, -1))[0]
        ends_idx = starts_idx - 1
        ends_idx[-1] = len(peak_pos_samples) - 1
        regions = pd.DataFrame(
            data=[
                peak_pos_samples[starts_idx[:-1]],
                peak_pos_samples[ends_idx[1:]],
                starts_idx[:-1],
                ends_idx[1:],
            ],
            index=["start_sample", "end_sample", "start_peak", "end_peak"],
        ).T

        for row, region in regions.iterrows():
            regions.at[row, "gait"] = True

        gait_bouts = (
            regions.where(regions["gait"] == True)
            .dropna()
            .drop(["start_peak", "end_peak", "gait"], axis=1)
        )
        return gait_bouts

    def apply_pdkit_segmentation(
        self, data: pd.DataFrame, sampling_rate_hz: float, n_segments: int=8
    ) -> pd.DataFrame:
        data = self._reformat_data(data, sampling_rate_hz)

        gp = GaitProcessor(
            sampling_frequency=sampling_rate_hz, filter_order=4, cutoff_frequency=1
        )
        data = gp.resample_signal(data)
        data_filtered = gp.filter_data_frame(data, centre=True, keep_cols=["td"])

        peak_pos_samples, prominences, clusters = gp.bellman_segmentation(
            data_filtered["acc_x"], n_segments+1
        )

        gait_bouts = self._get_gaitbouts_from_clusters(
            peak_pos_samples, prominences, clusters
        ).astype(int)

        return gait_bouts
