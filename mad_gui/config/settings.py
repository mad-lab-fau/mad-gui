class BaseSettings:
    BIND_Y_AXIS = True
    SENSORS_SYNCHRONIZED = True

    ACTIVITIES = {"gait": {"slow": None, "fast": ["jogging", "running"]}, "other": None}
    DETAILS = []

    STRIDE_SNAP_TO_MIN = False
    # SNAP_RANGE_S = 0.05  # in seconds
    # SNAP_CHANNEL = "AVERAGE_PUPIL_SIZE"

    PLOT_WIDTH_PLAYING_VIDEO = 20  # in seconds

    # CHANNELS_TO_PLOT = ["acc_x", "acc_y"]
