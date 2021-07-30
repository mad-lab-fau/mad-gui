"""Base class for importing and processing sensor data and annotations."""

import datetime
from pathlib import Path

import pandas as pd

from mad_gui.components.dialogs.user_information import UserInformation
from typing import Dict, Tuple, Union


class BasePlugin:
    """All plugins inherit from this."""

    def __init__(self, parent=None):
        self.parent = parent

    @classmethod
    def name(cls) -> str:
        raise NotImplementedError()


class BaseImporter(BasePlugin):
    """Classes based on this one enable the GUI to handle data from different systems."""

    @classmethod
    def name(cls) -> str:
        raise NotImplementedError()

    def load_sensor_data(self, file: str) -> Tuple[Dict, float]:  # noqa
        """Loading sensor data as it is usually stored by your recording device

        Parameters
        ----------
        file
            Full path to the file that should be used to load data.

        Returns
        -------
        sensor_data
            A dictionary with one key per sensor. Each of those, keeps a dataframe with one column per sensor channel.
            If the data consists of acc_x, acc_y, and acc_z the dataframe has three columns.
        sampling_rate_hz
            The sampling rate with which the data has been recorded.

        Examples
        --------
        >>> data, sr = load_sensor_data("/some/file.format")
        >>> data.keys()
        dict_keys(['left_sensor', 'right_sensor'])
        >>> sr
        102.4
        >>> data['left_sensor']
            acc_x    'acc_y'
        0    9.81       0.1
        1    9.80       0.0
        2    9.82       0.1

        """
        UserInformation.inform(
            "The functionality of loading sensor data is not implemented for the chosen importer / recording system."
        )
        raise NotImplementedError()

    def load_annotations(self, file_path: Union[Path, str]) -> Dict[str, pd.DataFrame]:  # noqa
        """This loads the list of stride and activity annotations from file_path.

        This method is called by the :class:`~mad_gui.LoadDataWindow` in case the user selects a file using the
        "Select annotation" button. In that case, this method should open the file specified by `file_path` and then
        create.

        NOTE: Your importer does not have to implement this method in case you do not want to deliver such
        functionality to the user.

        Parameters
        ----------
        file_path
            file_path to load the annotation data from

        Returns
        -------
        activity_dict
            Dictionary with keys being the titles of the plots in the main window.
            Each of them keeps a pd.DataFrame as it would be produced by
            :func:`mad_gui.plot_tools.SensorPlot.get_labels_from_plot`.
            This means the dataframe should at least have at least the columns `start` and `end`.

        Examples
        --------
        >>> annotations = load_annotations("/some/file.format")
        >>> annotations.keys()
        dict_keys(['left_sensor', 'right_sensor'])
        >>>annotations['left_sensor']
            label_id    start    end    description    details
        0          0      100    105           gait       fast
        1          1      105    108           gait       slow
        2          2      120    130       standing        NaN
        """
        UserInformation.inform(
            f"The functionality of loading annotations is not implemented for the chosen importer / recording system "
            f"({self.name()})."
        )
        raise NotImplementedError()

    def annotation_from_data(self, plot_data) -> Dict[str, pd.DataFrame]:  # noqa
        """Get labels from the data using an algorithm.

        This method uses the passed data and an algorithm to find specific activities.
        For example it could be a peak detection algorithm, which then for example creates one
        :class:`mad_gui.plot_tools.StrideLabel` between to consecutive peaks.
        You only need to implement this method, if you want to put a functionality behind the `Use algorithm` button.

        Parameters
        ----------
        data
            sensor data of one of the plots in MainWindow.sensor_plots
        sampling_rate_hz
            The sampling frequency for that plot

        Returns
        -------
        df
            A dataframe which can be processed by  :func:`mad_gui.plot_tools.SensorPlot._set_stride_labels`. Therefore,
            it should at least have the columns "start" and "end". Each row then corresponds to one stride
            label. Optionally, you can pass the colums "type" and/or "details" for each row / stride.
        """
        # df = some method that uses sensor data to get all the starts and ends for single activities / strides
        # return df
        UserInformation(parent=self.parent).inform(
            "The functionality of using an algorithm is not implemented for the chosen importer / recording system."
        )
        raise NotImplementedError()

    def get_start_time(self, *args, **kwargs) -> datetime.time:  # noqa
        """Get the start time of the corresponding data.

        This may be used by :class:`mad_gui.plot_tools.SensorPlot` to set the channel labels. However, you do not
        necessarily have to implement it. If you do not implement it, the x-channel will simply start at 0 seconds.

        NOTE: Your importer does not have to implement this method. If you do not implement it, the first sample of
        the shown data will be displayed at second 0 and the x-channel is going to be in seconds.

        Parameters
        ----------
        sensor_data_path
            The path of the sensor data that should be displayed in :class:`mad_gui.MainWindow`
        """
        # Implementing this for backward compa
        return None

    @staticmethod
    def get_sync_file(video_file: str) -> str:
        files = list(Path(video_file).parent.glob("*sync*.xlsx"))
        if len(files) == 0:
            UserInformation.inform(text="Video and data not synchronized because not sync file was found.")
            return None
        if len(files) == 1:
            return files[0]
        UserInformation.inform(
            text="Please make sure there is exactly one file that contains `sync` in its name and "
            "ends with "
            "`.xlsx`."
        )
        return None

    def get_video_signal_synchronization(self, video_file: str) -> pd.DataFrame:  # noqa
        """Searches for an excel file that has `sync` in its name and returns the sync indices from there.

        The Excel file should have as first column (index) "start_sample" and "end_sample" and the columns should be
        "video_frame" and "signal_sample."

        Attributes
        ----------
        video_file
            The path of the video that is being shown.

        Returns
        -------
        sync_indices
            A dataframe which tells the gui which frames of the video correspond to which samples in the signal.
            Currently only implemented to accept two synchronized events. Between those, the GUI interpolates linearly.
        """
        sync_file = self.get_sync_file(video_file)
        try:
            sync = pd.read_excel(sync_file, index_col=0, engine="openpyxl")
            return sync
        except IndexError:
            UserInformation.inform("Format of the sync file is unknown.")


class BaseExporter(BasePlugin):
    """Export gait data"""

    @classmethod
    def name(cls) -> str:
        raise NotImplementedError()

    def export(self, global_data):  # pylint: disable=unused-argument
        """Export data using a Plugin-Exporter.

        Parameters
        ----------
        global_data
            The GUI's :class:`mad_gui.models.global_data.GlobalData` object, which is kept in
            :class:`mad_gui.windows.main.MainWindow`
        """
        # we ignore `unused-argument` because maybe some exporter needs this
        UserInformation(parent=self.parent).inform(
            "The functionality to calculate parameters from plotted data is not implemented for "
            "the chosen exporter / recording system."
        )
