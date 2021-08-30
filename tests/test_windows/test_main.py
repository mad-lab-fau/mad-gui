import os
import sys
from pathlib import Path

import pytest
from mad_gui.models.global_data import PlotData
from mad_gui.plugins.example import ExampleImporter
from mad_gui.state_keeper import StateKeeper
from PySide2.QtCore import Qt, QTimer

from tests.test_windows.create_main_window import get_main_window


class TestGui:
    def test_open_gui(self, qtbot):
        """Test if it works to open and close the GUI"""

        gui = get_main_window()
        qtbot.addWidget(gui)
        assert not gui.is_data_plotted()
        gui.close()

    def test_toggle_menu(self, qtbot):
        gui = get_main_window()
        qtbot.addWidget(gui)
        assert not gui.ui_state.menu_collapsed
        qtbot.mouseClick(gui.ui.btn_toggle_menu, Qt.LeftButton)
        assert gui.ui_state.menu_collapsed
        qtbot.mouseClick(gui.ui.btn_toggle_menu, Qt.LeftButton)
        assert not gui.ui_state.menu_collapsed
        gui.close()

    @pytest.mark.parametrize(
        "load_sensor, load_activities, load_strides",
        [(True, True, True), (True, False, False)],
    )
    def test_load_data_from_pickle(self, qtbot, load_sensor, load_activities, load_strides):
        gui = get_main_window()
        qtbot.addWidget(gui)
        example_pickle = Path(__file__).parent.parent.parent / "example_data" / "data.mad_gui"

        def handle_dialog():
            for box_name, indicator in [
                ("sensor", load_sensor),
                ("ActivityLabel", load_activities),
                ("StrideLabel", load_strides),
            ]:
                gui.data_selector.boxes[box_name].setChecked(indicator)

            gui.data_selector.ok_btn.buttons()[0].clicked.emit()

        QTimer.singleShot(1500, handle_dialog)

        gui.load_data_from_pickle(str(example_pickle))

        # currently gui.plotted_data is empty, it is just in gui.global_data.plotted_data
        activities = {
            "Acceleration": gui.global_data.plot_data["Acceleration"].annotations["ActivityLabel"],
        }
        strides = {
            "Acceleration": gui.global_data.plot_data["Acceleration"].annotations["StrideLabel"],
        }

        if load_activities:
            assert len(activities["Acceleration"].data) == 1
        else:
            assert len(activities["Acceleration"].data) == 0
        if load_strides:
            assert len(strides["Acceleration"].data) == 1
            # assert strides["Acceleration"].iloc[0].start == 502
            # assert strides["Acceleration"].iloc[0].end == 560
            # _, sr = gui._get_sensor_data()
            # assert int(sr["Acceleration"]) == 50
        else:
            assert len(strides["Acceleration"].data) == 0
        gui.close()

    def test_toggle_label_state(self, qtbot):
        gui = get_main_window()
        imu_file = Path(__file__).parent.parent.parent / "example_data" / "acceleration.csv"
        video_file = Path(__file__).parent.parent.parent / "example_data" / "video" / "video.mp4"

        gui.global_data.data_file = str(imu_file)
        gui.global_data.video_file = str(video_file)
        qtbot.addWidget(gui)

        assert gui.VideoWindow.isHidden()
        gui.load_video(str(video_file))

        # wait until data is plotted
        qtbot.wait(1000)

        assert len(gui.sensor_plots) == 0
        sensor_data, sampling_rate = ExampleImporter().load_sensor_data(imu_file)
        plot_data = PlotData().from_dict({"data": sensor_data["Acceleration"], "sampling_rate_hz": sampling_rate})
        gui.global_data.plot_data = {"Acceleration": plot_data}
        qtbot.keyClick(gui, Qt.Key_A)
        qtbot.wait(1000)
        assert gui.plot_state.mode == "add"
        assert gui.ui.btn_add_label.isChecked()  # for some reason this stopped working in combination with doit...
        assert not gui.ui.btn_edit_label.isChecked()
        assert not gui.ui.btn_remove_label.isChecked()

        qtbot.keyClick(gui, Qt.Key_E)
        assert gui.plot_state.mode == "edit"
        assert not gui.ui.btn_add_label.isChecked()
        assert gui.ui.btn_edit_label.isChecked()
        assert not gui.ui.btn_remove_label.isChecked()

        qtbot.keyClick(gui, Qt.Key_R)
        assert gui.plot_state.mode == "remove"
        assert not gui.ui.btn_add_label.isChecked()
        assert not gui.ui.btn_edit_label.isChecked()
        assert gui.ui.btn_remove_label.isChecked()
        gui._save_sync = self.save_sync

        # self.video_duration_checked = False
        # if not os.environ.get("GITHUB_CI"):
        #    # video playing does not work on remote and thus also plot syncing
        StateKeeper.video_duration_available.connect(lambda duration: self.check_plot_length(gui, duration))
        qtbot.keyClick(gui, Qt.Key_S)
        qtbot.wait(2500)
        assert gui.plot_state.mode == "sync"
        assert not gui.ui.btn_add_label.isChecked()
        assert not gui.ui.btn_edit_label.isChecked()
        assert not gui.ui.btn_remove_label.isChecked()
        assert gui.ui.btn_sync_data.isChecked()
        assert gui.sensor_plots["Acceleration"].sync_item
        # TODO: really check video duration
        self.video_duration_checked = True
        # else:
        #    self.video_duration_checked = True

        qtbot.keyClick(gui, Qt.Key_Escape)
        qtbot.wait(2500)
        assert gui.plot_state.mode == "investigate"
        assert not gui.ui.btn_add_label.isChecked()
        assert not gui.ui.btn_edit_label.isChecked()
        assert not gui.ui.btn_remove_label.isChecked()
        assert not gui.sensor_plots["Acceleration"].sync_item

        gui.close()
        assert self.video_duration_checked

    def check_plot_length(self, gui, duration):
        assert gui.ui.video_plot.data[-1] == duration
        self.video_duration_checked = True

    @staticmethod
    def save_sync():
        print("This would actually call a dialog in mad_gui.windows.main._save_sync.")
