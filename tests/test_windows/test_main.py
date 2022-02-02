from pathlib import Path

import pytest
from PySide2.QtCore import Qt, QTimer

from mad_gui.models.global_data import PlotData
from mad_gui.plugins.example import ExampleImporter
from tests.test_windows.create_main_window import get_main_window

SENSOR_NAME = "Pocket IMU"


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
        "load_sensor, load_activities",
        [(True, True), (True, False)],
    )
    def test_load_data_from_pickle(self, qtbot, load_sensor, load_activities):
        gui = get_main_window()
        qtbot.addWidget(gui)
        example_pickle = Path(__file__).parent.parent.parent / "example_data" / "data.mad_gui"

        def handle_dialog():
            for box_name, indicator in [
                ("sensor_data", load_sensor),
                ("Peak", False),
                ("Activity", load_activities),
            ]:
                gui.data_selector.boxes[box_name].setChecked(indicator)

            gui.data_selector.ok_btn.buttons()[0].clicked.emit()

        QTimer.singleShot(1500, handle_dialog)

        gui.load_data_from_pickle(str(example_pickle))

        # currently gui.plotted_data is empty, it is just in gui.global_data.plotted_data
        activities = {
            SENSOR_NAME: gui.global_data.plot_data[SENSOR_NAME].annotations["Activity"],
        }

        if load_activities:
            assert len(activities[SENSOR_NAME].data) == 1
        else:
            assert len(activities[SENSOR_NAME].data) == 0
        gui.close()

    def test_toggle_label_state(self, qtbot):
        gui = get_main_window()
        imu_file = Path(__file__).parent.parent.parent / "example_data" / "sensor_data.csv"
        video_file = Path(__file__).parent.parent / "test_video.mp4"

        gui.global_data.data_file = str(imu_file)
        gui.global_data.video_file = str(video_file)
        qtbot.addWidget(gui)
        qtbot.wait(1000)
        assert gui.VideoWindow.isHidden()
        gui.load_video(str(video_file))

        # wait until data is plotted
        qtbot.wait(1000)

        assert len(gui.sensor_plots) == 0
        plot_data_dict = ExampleImporter().load_sensor_data(imu_file)
        plot_data = PlotData.from_dict(
            {
                "sensor_data": plot_data_dict[SENSOR_NAME]["sensor_data"],
                "sampling_rate_hz": plot_data_dict[SENSOR_NAME]["sampling_rate_hz"],
            }
        )
        gui.global_data.plot_data = {SENSOR_NAME: plot_data}
        gui._enable_buttons(True)
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

        qtbot.keyClick(gui, Qt.Key_S)
        qtbot.wait(2500)
        assert gui.plot_state.mode == "sync"
        assert not gui.ui.btn_add_label.isChecked()
        assert not gui.ui.btn_edit_label.isChecked()
        assert not gui.ui.btn_remove_label.isChecked()
        assert gui.ui.btn_sync_data.isChecked()
        assert gui.sensor_plots[SENSOR_NAME].sync_item
        qtbot.wait(2500)
        if gui.video_plot:
            # for some reason this does not yet work on the remote, but only locally
            assert not gui.video_plot.isHidden()

        qtbot.keyClick(gui, Qt.Key_Escape)
        qtbot.wait(2500)
        assert gui.plot_state.mode == "investigate"
        assert not gui.ui.btn_add_label.isChecked()
        assert not gui.ui.btn_edit_label.isChecked()
        assert not gui.ui.btn_remove_label.isChecked()
        assert not gui.sensor_plots[SENSOR_NAME].sync_item
        gui.close()

    @staticmethod
    def save_sync():
        print("This would actually call a dialog in mad_gui.windows.main._save_sync.")
