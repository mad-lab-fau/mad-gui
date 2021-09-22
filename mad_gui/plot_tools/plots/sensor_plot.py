import datetime
import warnings

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PySide2.QtCore import QObject, Qt, QTime, Slot
from PySide2.QtUiTools import loadUiType
from PySide2.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QMenu,
    QRadioButton,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)

from mad_gui.config import Config
from mad_gui.models.local import PlotData
from mad_gui.models.ui_state import MODES
from mad_gui.plot_tools.labels import BaseRegionLabel
from mad_gui.plot_tools.labels.base_label import BaseEventLabel
from mad_gui.plot_tools.plots.base_plot import BasePlot
from mad_gui.plot_tools.plots.sensor_plot_mode_handler import (
    AddModeHandler,
    BaseModeHandler,
    EditModeHandler,
    InvestigateModeHandler,
    RemoveModeHandler,
    SyncModeHandler,
)
from mad_gui.qt_designer import UI_PATH
from mad_gui.state_keeper import StateKeeper
from mad_gui.utils.helper import resource_path
from mad_gui.utils.model_base import BaseStateModel, Property
from typing import Callable, Dict, List, Optional, Type, Union

channel_selector_path = str(UI_PATH / "channel_selector.ui")
ui_path = resource_path(channel_selector_path)
if ".ui" in ui_path:
    ChannelSelector, _ = loadUiType(ui_path)
elif ".py" in ui_path:
    from mad_gui.qt_designer.build.channel_selector import Ui_Form as ChannelSelector  # noqa


class TimeAxisItem(pg.AxisItem):
    """Class to show the time hh:mm:ss on x-channel instead of seconds since start.

    Parameters
    ----------
    start_time
        the time at which the session recording started

    Notes
    -----
    Please be aware that this assumes equal time deltas between all samples. This might lead to the fact,
    that for long datasets the actual time does not align with the our calculation from the samples. To give you a
    rough idea, in a dataset of 2h length, we are approximately off by 3-4 seconds.
    """

    def __init__(self, start_time: QTime, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = start_time
        self.parent = parent

    def tickStrings(self, values: List, *args):  # noqa
        # note, that the received values are seconds
        ms = np.array(values) * 1000
        self.parent.configure_style()
        return [self.start_time.addMSecs(value).toString("hh:mm:ss") for value in ms]


class SensorPlotState(BaseStateModel):
    plot_channels = Property([], dtype=list)
    mode: MODES = Property("investigate", dtype=str)


class SensorPlot(BasePlot):
    """Can be used to visualize IMU data and to create, delete and interact with plotted labels.

    Parameters
    ----------
    parent
        Parent widget or frame
    """

    MODE_HANDLER: Dict[MODES, Type[BaseModeHandler]] = {
        "add": AddModeHandler,
        "investigate": InvestigateModeHandler,
        "edit": EditModeHandler,
        "remove": RemoveModeHandler,
        "sync": SyncModeHandler,
    }

    def __init__(
        self,
        plot_data: PlotData,
        initial_plot_channels=Optional[List[str]],
        start_time=Optional[datetime.datetime],
        label_classes=List[BaseRegionLabel],
        event_classes: Optional[List[BaseEventLabel]] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(
            plot_data=plot_data,
            initial_plot_channels=initial_plot_channels,
            label_classes=label_classes,
            event_classes=event_classes,
            parent=parent,
        )
        self.start_time = start_time
        self.is_main_plot = False

        self._skip_snap_to = False
        self.state = SensorPlotState()
        self.state.plot_channels = initial_plot_channels or list(plot_data.data.columns)
        # We set the data once with auto range and all further updates don't update the range again.
        self._set_plot_data(
            self.plot_data.data,
            self.plot_data.sampling_rate_hz,
            self.state.plot_channels,
            fix_channels=False,
            start_time=self.start_time,
        )
        if len(plot_data.data) > 10000 and getattr(Config.settings, "AUTO_DOWNSAMPLE", False):
            self.plotItem.setDownsampling(auto=True)
        self.plotItem.setClipToView(True)
        self.state.bind(
            Slot(list)(
                lambda x: self._set_plot_data(
                    self.plot_data.data,
                    self.plot_data.sampling_rate_hz,
                    x,
                    fix_channels=True,
                    start_time=self.start_time,
                )
            ),
            "plot_channels",
            initial_set=False,
        )

        self.mode_handler = InvestigateModeHandler(self)
        self.state.bind(self._change_mode, "mode", initial_set=True)

        self._add_channel_selection_menu()
        StateKeeper.video_window_closed.connect(self.remove_video_cursor_line)

    #    for label in label_classes:
    #        self.plot_data.annotations[label.name].bind(lambda x: self._plot_annotations(x, label), "data")

    # def _plot_annotations(self, data, label_class):
    #    self.clear_labels(label_class)
    #    for _, label in data.iterrows():
    #        label = label_class(start=label.start, end=label.end, description=label.description, parent=self)
    #        self.addItem(label)

    def adapt_to_opening_video_window(self):
        if self.sync_info is not None:
            self.add_video_cursor_line()
            self.autoRange()
            StateKeeper.data_position_changed.connect(self.move_video_cursor_line)
            StateKeeper.data_position_changed.connect(self.set_graph_position)

    def _update_plotted_channels(self):
        submenus = self.getPlotItem().vb.menu.ctrl
        menu = next(iter([menu for menu in submenus if isinstance(menu, ChannelSelector)]))
        self.state.plot_channels = [
            cb.objectName() for cb in menu.channel_names.findChildren(QCheckBox) if cb.isChecked()
        ]

    def _add_channel_selection_menu(self):
        # adapted from pg.graphicsItems.ViewBox.channelCtrlTemplate
        submenu = QMenu()
        submenu.setTitle("Select channels")
        widget = QWidget()
        ui = ChannelSelector()
        ui.setupUi(widget)
        ui.label_help.setOpenExternalLinks(True)
        # open on hovering
        action = QWidgetAction(self.getPlotItem().vb.menu)
        action.setDefaultWidget(widget)
        submenu.addAction(action)
        self.channels_selection_button_group = QButtonGroup(parent=ui.channel_names_layout, objectName="channelsWidget")
        self.channels_selection_button_group.setExclusive(False)
        for channel in self.plot_data.data.columns:
            cb = QCheckBox(channel)
            cb.setCheckState(Qt.Checked if channel in self.state.plot_channels else Qt.Unchecked)
            cb.setObjectName(channel)
            self.channels_selection_button_group.addButton(cb)
            ui.channel_names_layout.addWidget(cb)

        self.channels_selection_button_group.buttonToggled.connect(self._update_plotted_channels)

        # add to plotwidget
        self.getPlotItem().vb.menu.axes.append(submenu)
        self.getPlotItem().vb.menu.ctrl.append(ui)
        self.getPlotItem().vb.menu.widgetGroups.append(submenu)
        self.getPlotItem().vb.menu.addMenu(submenu)

    def is_data_plotted(self):
        plotted_data = self.getPlotItem().listDataItems()
        if plotted_data and plotted_data[0].getData()[0] is not None:
            return True
        return False

    def _set_plot_data(
        self,
        data: pd.DataFrame,
        sampling_rate_hz: float,
        channels_to_plot: List[str],
        fix_channels: bool = False,
        start_time: Optional[datetime.time] = None,
    ):
        """Plot data into the widget. Will erase previous plotted data.

        Parameters
        ----------
        data
            Contains sensor data that should be plotted. The default channels to be plotted can be set in the config
            file :mod:`mad_gui.config` by setting the variable "CHANNELS_TO_PLOT", see also :ref:`Setting constants
            <channels to_plot>`.
        sampling_rate_hz
            Sampling frequency of the passed data in unit of Hertz
        fix_channels
            If true, it will not reset the x/y-channel to all available data but keep the current limits
            (x_min and x_max).
        start_time
            If you pass a start time, the x-channel will not show seconds from start of the recording but the time of
            the day
        """
        if data is None:
            return

        self._clear_data()
        ax_bottom = self.getAxis("bottom")
        ax_bottom.setLabel(text="time [seconds]")

        if not isinstance(data.index[0], int):
            raise TypeError(
                f"The index of the dataframe created by a loader must contain integers. However, "
                f"in this case it contained {type(data.index[0])}. You may change that by using "
                f"`df.reset_index(drop=True)` in your loaders `load_sensor_data`."
            )
        x_axis = data.index / sampling_rate_hz
        if start_time:
            start_time_qt = QTime(start_time.hour, start_time.minute, start_time.second)
            channel_items = {"bottom": TimeAxisItem(start_time_qt, orientation="bottom", parent=self)}
            self.setchannelItems(channel_items)
            ax_bottom = self.getchannel("bottom")
            ax_bottom.setLabel(text="time [hh:mm:ss]")
        colors_fau = list(Config.theme.FAU_PHILFAK_COLORS.values())
        colors_fau.extend(Config.theme.FAU_NATFAK_COLORS.values())
        colors_fau.extend(Config.theme.FAU_COLORS.values())

        if fix_channels:
            self.disableAutoRange()
        else:
            self.enableAutoRange()

        for channel_name in channels_to_plot:
            # make sure we use the same color for one channel even if only few channels are plotted
            color_index = np.argmax([channel_name == item for item in data.columns])
            color = colors_fau[color_index]

            data_to_plot = data[channel_name]
            if getattr(Config.settings, "NORMALIZE_DISPLAYED_DATA", False) is True:
                data_zero_mean = data_to_plot - data_to_plot.mean()
                data_to_plot = data_zero_mean / (data_zero_mean.max() - data_zero_mean.min())
            try:
                self.plot(
                    x=x_axis,
                    y=data_to_plot,
                    pen=pg.mkPen(width=2, color=color),
                )
            except TypeError:
                warnings.warn(f"Cannot plot channel {channel_name} because of a type error.")

        self.autoRange()

        # make it responsive even for zoomed-in large datasets
        self.getPlotItem().setClipToView(True)

    def _change_mode(self, new_mode: MODES):
        """Adapt tool tip text depending on mode and remove potentially plotted green line indicating a new event.

        Parameters
        ----------
        new_mode
            One of `add`, `edit`, `remove`, or `investigate`
        """
        # Deactivate old mode_handler:
        self.mode_handler.deactivate()
        self.mode_handler = self.MODE_HANDLER[new_mode](sensor_plot=self)
        self.set_tooltip(new_mode)

        # On mode change, we sync the annotation state:
        self._sync_annotations()

    def _sync_annotations(self):
        for label_class in self.label_classes:
            self.plot_data.annotations[label_class.name].data = self._get_labels_from_plot(label_class)
        self.plot_data.annotations["events"].data = self._get_events_from_plot(BaseEventLabel)

    def set_tooltip(self, mode: MODES):
        tips = {
            "add": "Click to set position of start / event / end",
            "edit": "Hover over a line to be moved or click on a label to edit its type / details",
            "investigate": "Zoom by hovering over channels and scrolling",
            "remove": "Hover over label to remove and click left mouse",
            "sync": "Move the lines such that\n   - the green lines indicate moments at which all data streams are at "
            "the start position\n   - the red lines indicate moments at which all data streams are at the end "
            "position",
        }
        self.setToolTip(tips[mode])

    def clear_labels(self, label_class):
        for item in self.items():
            if type(item) == label_class:  # pylint: disable=unidiomatic-typecheck
                # we need this kind of type check since stride labels inherit from activity labels and thus would also
                # be selected if using `isinstance(...)`
                self.delete_item(item)

    def _clear_data(self):
        for item in self.items():
            if isinstance(item, pg.graphicsItems.PlotDataItem.PlotDataItem):
                self.delete_item(item)

    def delete_item(self, item: QObject):
        if self.event_labels:
            for event in self.event_labels.values():
                self.parent.removeItem(event)
        self.removeItem(item)

    def keyPressEvent(self, ev):  # noqa
        # Camelcase method overwrites qt method
        self.mode_handler.handle_key_press(ev)
        # This is important! As it will forward unhandled events to the parent!
        super().keyPressEvent(ev)

    def mousePressEvent(self, ev):  # noqa
        # Camelcase method overwrites qt method
        self.mode_handler.handle_mouse_click(ev)

    def mouseMoveEvent(self, ev):  # noqa
        # Camelcase method overwrites qt method
        self.mode_handler.handle_mouse_movement(ev)

    def _snap_to(self, pos: float, f: Callable):
        if self._skip_snap_to:
            return pos
        sampling_rate = self.plot_data.sampling_rate_hz
        pos_sample = pos * sampling_rate
        snap_min = int(pos_sample - getattr(Config.settings, "SNAP_RANGE_S", 0.1) / 2 * sampling_rate)
        snap_max = int(pos_sample + getattr(Config.settings, "SNAP_RANGE_S", 0.1) / 2 * sampling_rate)
        if not hasattr(Config.settings, "SNAP_CHANNEL"):
            ds = SelectSnapChannel(parent=self.parent, channels=list(self.plot_data.data.columns))
            ds.ask_user()
            snap_channel, remember = ds.get_snap_channel()
            if not snap_channel:
                return pos
            del ds
            if remember:
                Config.settings.SNAP_CHANNEL = snap_channel
        else:
            snap_channel = Config.settings.SNAP_CHANNEL
        region_data = self.plot_data.data[snap_channel].iloc[snap_min:snap_max]
        values = region_data.values
        idx_relative = f(values)
        idx_absolute = region_data.index[idx_relative]
        return idx_absolute / sampling_rate

    def snap_to_max(self, pos: float):
        """Snap to a maximum in the `Config.settings.SNAP_CHANNEL` of the sensor.

        Parameters
        ----------
        pos
            Position on the x-channel given in seconds

        Returns
        -------
        pos_snapped
            maximum within pos +- SNAP_RANGE_S (in seconds)/2 defined in your settings.
        """
        return self._snap_to(pos, np.argmax)

    def snap_to_min(self, pos: float):
        """Snap to a minimum in the `Config.settings.SNAP_CHANNEL` of the sensor.

        Parameters
        ----------
        pos
            Position on the x-channel given in seconds

        Returns
        -------
        pos_snapped
            minimum within pos +- SNAP_RANGE_S (in seconds)/2 defined in your settings.
        """
        return self._snap_to(pos, np.argmin)

    @staticmethod
    def _get_appropriate_stride_id():
        # TODO: find the proper stride number and renumber strides in stride_list
        return 0

    def _iter_labels_from_plot(self, label_type: Type[Union[BaseRegionLabel, BaseEventLabel]]):
        """Finds all instances of label_type in the plot and returns them."""
        for i_item in self.items():
            if type(i_item) is label_type:  # noqa
                # I need to use type, because StrideLabel inherits RegionLabel and thus I can not differentiate
                # them using `isinstance`
                yield i_item

    def _get_events_from_plot(self, label_type: Type[BaseEventLabel]) -> pd.DataFrame:
        events = self._iter_labels_from_plot(label_type)
        event_dicts = []
        for event in events:
            if event.belongs_to_region_label:
                continue
            pos = event.pos()
            data_dict = {
                "pos": int(pos.x() * self.plot_data.sampling_rate_hz),
                "min_height": event.span[0],
                "max_height": event.span[1],
                "description": event.description,
            }
            # if issubclass(label_type, StrideLabel):
            #    data_dict.update({"tc": [int(label.lines[2].pos()[0] * self.sampling_rate_hz)]})
            event_dicts.append(data_dict)
        df = pd.DataFrame.from_records(event_dicts)
        if df.empty:
            return df
        df.sort_values(by="pos", axis=0, inplace=True)
        return df.reset_index(drop=True)

    def _get_labels_from_plot(self, label_type: Type[BaseRegionLabel]) -> pd.DataFrame:
        """Finds all labels of type label_type and formats them into a pandas.DataFrame

        Parameters
        ----------
        label_type
            Some class, either RegionLabel or a class, which inherits from it.

        Returns
        -------
        labels
            A pandas.DataFrame with the columns label_id, start, end, type and details (see
            :class:`~mad_gui.plot_tools.RegionLabel`).
            In case of `label_type` being :class:`~mad_gui.plot_tools.StrideLabel`, there is an additional column `tc` (
            terminal contact).

        See Also
        --------
        :func:~mad_gui.plot_tools.SensorPlot._sync_annotations` will use this to synchronize the plotted labels with
        the labels in :class:`mad_gui.models.global_data.PlotData` object, which then can be accessed via the
        GUI's :class:`mad_gui.models.global_data.GlobalData`.
        """
        labels = self._iter_labels_from_plot(label_type)
        label_dicts = []
        for label in labels:
            start, end = label.getRegion()

            data_dict = {
                "identifier": label.id,
                "start": int(start * self.plot_data.sampling_rate_hz),
                "end": int(end * self.plot_data.sampling_rate_hz),
                "description": label.description,
            }
            for event_name, event_label in label.event_labels.items():
                data_dict.update({event_name: event_label.pos().x() * self.plot_data.sampling_rate_hz})
            label_dicts.append(data_dict)
        df = pd.DataFrame.from_records(label_dicts)
        if df.empty:
            return df
        df.sort_values(by="start", axis=0, inplace=True)
        return df.reset_index(drop=True)


class SelectSnapChannel(QDialog):
    def __init__(self, parent=None, channels=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowModality(Qt.ApplicationModal)
        self.setPalette(self.parent.palette())
        self.vbox = QVBoxLayout()
        self.channels = channels
        self.add_checkboxes_to_vbox()
        self.add_ok_btn()
        self.remember = QCheckBox("Remember until closing GUI")
        self.remember.setStyleSheet(self.parent.ui.btn_add_label.styleSheet().replace("QPushButton", "QCheckBox"))
        self.vbox.addWidget(self.remember)
        self.setLayout(self.vbox)
        self.setWindowTitle("Select channel to use for snapping")

    def add_checkboxes_to_vbox(self):
        self.radio_buttons = {}
        for channel in self.channels:
            self.radio_buttons[channel] = QRadioButton(channel)
            self.radio_buttons[channel].setChecked(Qt.Unchecked)
            style = self.parent.ui.btn_add_label.styleSheet()
            self.radio_buttons[channel].setStyleSheet(style.replace("QPushButton", "QRadioButton"))
            self.vbox.addWidget(self.radio_buttons[channel])

    def get_snap_channel(self):
        for channel in self.channels:
            if self.radio_buttons[channel].isChecked():
                return self.radio_buttons[channel].text(), self.remember.isChecked()
        return None, None

    def add_ok_btn(self):
        self.ok_btn = QDialogButtonBox(QDialogButtonBox.Ok)
        button_style = self.parent.ui.btn_add_label.styleSheet()
        self.ok_btn.setStyleSheet(button_style)
        self.ok_btn.clicked.connect(self.handle_ok_click)
        self.vbox.addWidget(self.ok_btn)

    def handle_ok_click(self):
        self.close()

    def ask_user(self):
        self.exec_()
