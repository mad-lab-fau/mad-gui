from pathlib import Path

import pytest

from mad_gui.plugins.base import BaseFileImporter
from mad_gui.plugins.example import ExampleFileImporter

EXAMPLE_DATA_PATH = Path(__file__).parent.parent.parent / "example_data"


class TestBaseImporter:
    def test_instantiation(self):
        ExampleFileImporter()

    def test_not_implemented(self):
        with pytest.raises(NotImplementedError):
            importer = BaseFileImporter()
            importer.load_annotations("bad_path")

    def test_bad_path(self):
        with pytest.raises(FileNotFoundError):
            importer = ExampleFileImporter()
            importer.load_sensor_data("bad_path")

    def test_load_data(self):
        importer = ExampleFileImporter()
        print("Importer Created.")
        plot_data = importer.load_sensor_data(EXAMPLE_DATA_PATH / "sensor_data.csv")
        print("Data imported.")
        assert len(plot_data["Pocket IMU"]["sensor_data"]) == 5526
