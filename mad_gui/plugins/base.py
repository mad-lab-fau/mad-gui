"""Base class for importing and processing sensor data and annotations."""
import abc
import datetime
from pathlib import Path

import pandas as pd

from mad_gui.components.dialogs.user_information import UserInformation
from mad_gui.models.local import PlotData
from typing import Dict, Union


class BasePlugin:
    """All plugins inherit from this."""

    def __init__(self, parent=None):
        self.parent = parent

    @classmethod
    def name(cls) -> str:
        raise NotImplementedError()


class BaseImporter(BasePlugin):
    """Classes based on this one enable the GUI to load data from different systems/formats."""

    @classmethod
    @abc.abstractmethod
    def name(cls) -> str:
        raise NotImplementedError()

    def load_sensor_data(self, file: str) -> Dict:  # noqa
        """Loading sensor data as it is usually stored by your recording device

        Parameters
        ----------
        file
            Full path to the file that should be used to load data. You will automatically receive this from the GUI
            which calls this importer.

        Returns
        -------
        sensor_data
            A dictionary with one key per sensor. Each of those, again keeps a dictionary, with at least two keys:
            `sensor data` and `sampling_rate_hz`. Behind the key `sensor_data` is a pd.DataFrame with one column per
            channel, `sampling_rate_hz` is a float.
            If this dictionary has further keys, those will later be stored in
            :class:`mad_gui.models.local.PlotData`'s additional_data.

        Examples
        --------
        >>> data = load_sensor_data("/some/file.format")
        >>> data.keys()
        dict_keys(['left_sensor', 'right_sensor'])
        >>> data['left_sensor'].keys()
        dict_keys(['sensor_data', 'sampling_rate_hz'])
        >>> data['left_sensor']['sensor_data']
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

        This method is called by the :class:`~mad_gui.components.dialogs.plugin_selection.LoadDataDialog` in case the
        user selects a file using the "Select annotation" button. In that case, this method should open the file
        specified by `file_path` and then create.

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
            :func:`mad_gui.plot_tools.plots.SensorPlot.get_labels_from_plot`.
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

    def get_start_time(self, *args, **kwargs) -> datetime.time:  # noqa
        """Get the start time of the corresponding data.

        This may be used by :class:`mad_gui.plot_tools.plots.SensorPlot` to set the channel labels. However, you do not
        necessarily have to implement it. If you do not implement it, the x-channel will simply start at 0 seconds.

        NOTE: Your importer does not have to implement this method. If you do not implement it, the first sample of
        the shown data will be displayed at second 0 and the x-channel is going to be in seconds.

        Parameters
        ----------
        sensor_data_path
            The path of the sensor data that should be displayed in :class:`mad_gui.windows.MainWindow`
        """
        # Implementing this for backward compa
        return None

    @staticmethod
    def _get_sync_file(video_file: str) -> str:
        files = list(Path(video_file).parent.glob("*sync*.xlsx"))
        if len(files) == 0:
            UserInformation.inform(
                text="Video and data not synchronized because not sync file was found.",
                help_link="https://mad-gui.readthedocs.io/en/latest/troubleshooting.html#video-and"
                "-data-not-synchronized",
            )
            return None
        if len(files) == 1:
            return files[0]
        UserInformation.inform(
            text="Please make sure there is exactly one file that contains `sync` in its name and "
            "ends with "
            "`.xlsx`."
        )
        return None

    def _get_video_signal_synchronization(self, video_file: str) -> pd.DataFrame:  # noqa
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


class BaseAlgorithm(BasePlugin):
    """A base class for implementing an algorithm. """

    @classmethod
    @abc.abstractmethod
    def name(cls) -> str:
        return "Basic Algorithm"

    @abc.abstractmethod
    def process_data(self, plot_data: Dict[str, PlotData]):  # noqa
        """Get labels from the data using an algorithm.

        This method applies an algorithm to the passed data.
        For example it could be a peak detection algorithm, which then for example creates one
        :class:`mad_gui.plot_tools.labels.BaseRegionLabel` between to consecutive peaks.
        This method can be accessed by the user by clicking the `Use algorithm` button in the GUI's sidebar.
        For more information and an example, see the part of `Implement an algorithm
        <https://mad-gui.readthedocs.io/en/latest/customization.html#implement-an-algorithm>`_
        in our online documentation.

        Parameters
        ----------
        data
            A dictionary, where keys are the names of the plots in the GUI and the values are instances of
            :class:`mad_gui.models.local.PlotData`. These in turn keep the plotted sensor data, its sampling frequency,
            and the plotted annotations.

        Returns
        -------
        data
            The passed `data`, which you have adapted, e.g. by adding annotations or changing annotations.

        """
        # df = some method that uses sensor data to get all the starts and ends for single activities / strides
        # return df
        raise NotImplementedError()


class BaseExporter(BasePlugin):
    """Export gait data"""

    @classmethod
    @abc.abstractmethod
    def name(cls) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def process_data(self, global_data):
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
        raise NotImplementedError()
