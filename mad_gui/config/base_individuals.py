from mad_gui.plot_tools.labels import SegmentedStrideLabel

AXES_TO_PLOT = ["acc_x", "acc_y"]

# class Label(BaseRegionLabel):
#    name = "Normal Label"
#    color = "red"
#    snap_to_min = True
#    min_height = 20
#    max_height = 80
#    annotation = {"gait": ["fast", "slow"], "other": None}

# LABEL_CONFIG = {"Stride": RegionLabel} # wenn kein min_height: an anderer stelle

# LABEL_CONFIG an Plot Objekt übergeben -> Datenstrukutr (min_height, max_height): "Stride"
# class_object = item.pop("class")
# class_instance = class_object(**item)


STRIDE_LABEL_CLASS = SegmentedStrideLabel
STRIDE_SNAP_TO_MIN = False
SNAP_RANGE_S = 0.1  # in seconds

MAX_HEIGHT_STRIDE_LABELS = 0.8
MIN_HEIGHT_STRIDE_LABELS = 0.2
PLOT_WIDTH_PLAYING_VIDEO = 20  # in seconds
