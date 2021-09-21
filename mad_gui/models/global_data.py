from __future__ import annotations

from mad_gui.models.local import PlotData
from mad_gui.plot_tools.labels import BaseRegionLabel
from mad_gui.utils.model_base import BaseStateModel, Property
from typing import TYPE_CHECKING, Dict, List, Type

if TYPE_CHECKING:
    from mad_gui.plugins.base import BaseImporter, BasePlugin


class GlobalData(BaseStateModel):
    """A single object per MaD GUI instance that keeps global data.

    Attributes
    ----------
    active_loader
        One of the loaders passed to start_gui, which have inherited from :class:`~mad_gui.plugins.BaseImporter`. It
        can be selected by the user via the dropdown menu in the
        :class:`~mad_gui.components.dialogs.plugin_selection.LoadDataDialog`.
    data_file
        File of the data that is selected by the user in the
        :class:`~mad_gui.components.dialogs.plugin_selection.LoadDataDialog`.
    sync_file
        A file that keeps synchronization between video and sensor data. The GUI automatically searches for a file in
        the same folder as the video_file and if it finds a file, that has `*sync*.xlsx` in it assumes, this keeps
        the video synchronization.
    video_file
        File which contains the video to be displayed in the
        :class:`~mad_gui.components.dialogs.plugin_selection.LoadDataDialog`.
    plot_data
        A dictionary, where the keys are the names of the plots and the values are
        :class:`~mad_gui.models.local.PlotData` objects.
    plugins
        All plugins, that the GUI is aware of. The GUI is aware of all plugins that were passed to it via
        :meth:`~mad_gui.start_gui`.
    labels
        All the labels that the GUI is aware of (= the ones that were passed to :meth:`~mad_gui.start_gui`)

    """

    data_file = Property("", dtype=str)
    video_file = Property("", dtype=str)
    sync_file = Property("", dtype=str)
    annotation_file = Property("", dtype=str)
    base_dir = Property("", dtype=str)

    plot_data: Dict[str, PlotData] = Property({}, dtype=dict)

    # we need to initialize this for sphinx
    plugins: List[Type[BasePlugin]] = []
    labels: List[Type[BaseRegionLabel]] = []
    active_loader: BaseImporter = None
