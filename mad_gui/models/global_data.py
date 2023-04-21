"""A unique object per opened MaD GUI, keeping all relevant data."""

from __future__ import annotations

from mad_gui.models.local import PlotData
from mad_gui.utils.model_base import BaseStateModel, Property
from typing import Dict


class GlobalData(BaseStateModel):
    """A single object per MaD GUI instance that keeps global data.

    Attributes
    ----------
    active_loader
        One of the loaders passed to start_gui, which have inherited from :class:`~mad_gui.plugins.BaseFileImporter`. It
        can be selected by the user via the dropdown menu in the
        :class:`~mad_gui.components.dialogs.plugin_selection.FileLoaderDialog`.
    annotation_file
        In case the user selected annotations when loading data in the
        :class:`~mad_gui.components.dialogs.plugin_selection.FileLoaderDialog`, this keeps the file the user selected.
    data_file
        File of the data that is selected by the user in the
        :class:`~mad_gui.components.dialogs.plugin_selection.FileLoaderDialog`.
    sync_file
        A file that keeps synchronization between video and sensor data. The GUI automatically searches for a file in
        the same folder as the video_file and if it finds a file, that has `*sync*.xlsx` in it assumes, this keeps
        the video synchronization.
    video_file
        File which contains the video to be displayed in the
        :class:`~mad_gui.components.dialogs.plugin_selection.FileLoaderDialog`.
    plot_data
        A dictionary, where the keys are the names of the plots and the values are
        :class:`~mad_gui.models.local.PlotData` objects.
    plugins
        All plugins, that the GUI is aware of. The GUI is aware of all plugins that were passed to it via
        :meth:`~mad_gui.start_gui`.
    labels
        All the label classes that the GUI is aware of (= the ones that were passed to :meth:`~mad_gui.start_gui`).
        The actually plotted annotations can not be found here, but in `plot_data[<name of the
        plot>].annotations.data`,
        see the documentation of :class:`~mad_gui.models.local.PlotData`.

    """
    data_index = Property(None, dtype=int)
    data_label = Property("", dtype=str)
    data_file = Property("", dtype=str)
    video_file = Property("", dtype=str)
    sync_file = Property("", dtype=str)
    annotation_file = Property("", dtype=str)
    base_dir = Property("", dtype=str)

    # TODO: make plot_data a working property, so we do not need to call _plot_data manually after using
    #  MainWindow.use_algorithm.
    plot_data: Dict[str, PlotData] = Property({}, dtype=dict)
