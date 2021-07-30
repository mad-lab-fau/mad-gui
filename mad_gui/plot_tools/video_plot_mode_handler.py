from mad_gui.plot_tools.labels import BaseRegionLabel
from mad_gui.plot_tools.sensor_plot_mode_handler import BaseModeHandler
from mad_gui.state_keeper import StateKeeper


class SyncModeHandler(BaseModeHandler):
    def __init__(self, plot):
        super().__init__(plot)
        self.plot.remove_video_cursor_line()
        self.plot.add_video_cursor_line()
        self.plot.add_sync_item()
        self.plot.show()
        self.plot.video_window.player.positionChanged.connect(self.plot.move_video_cursor_line)
        for item in self.plot.items():
            if isinstance(item, BaseRegionLabel):
                item.make_editable()

    def deactivate(self):
        self.plot.distribute_video_sync()
        self.plot.finish_syncing()
        self.plot.hide()
        StateKeeper.save_sync.emit()
        self.plot.video_window.player.positionChanged.disconnect(self.plot.move_video_cursor_line)

        for item in self.plot.items():
            if isinstance(item, BaseRegionLabel):
                item.make_readonly()
