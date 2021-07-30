class BaseSettings:
    CHANNELS_TO_PLOT = ["acc_x", "acc_y"]

    BIND_Y_AXIS = True
    SENSORS_SYNCHRONIZED = True

    ACTIVITIES = ["gait", "other"]
    DETAILS = []

    STRIDE_LABEL_CLASS = "segmented_stride"
    STRIDE_SNAP_TO_MIN = False
    # SNAP_RANGE_S = 0.05  # in seconds
    # SNAP_CHANNEL = "AVERAGE_PUPIL_SIZE"

    MAX_HEIGHT_STRIDE_LABELS = 0.8
    MIN_HEIGHT_STRIDE_LABELS = 0.2
    PLOT_WIDTH_PLAYING_VIDEO = 20  # in seconds
