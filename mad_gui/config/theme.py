from PySide2.QtGui import QColor


class BaseTheme:
    FAU_COLORS = {
        "dark_blue": QColor(0, 56, 101),
        "medium_blue": QColor(144, 167, 198),
        "light_blue": QColor(221, 229, 240),
    }

    FAU_NATFAK_COLORS = {
        "dark": QColor(0, 155, 119),
        "medium": QColor(170, 207, 189),
        "light": QColor(229, 239, 234),
    }

    FAU_TECHFAK_COLORS = {
        "dark": QColor(152, 164, 174),
        "medium": QColor(210, 213, 215),
        "light": QColor(235, 236, 238),
    }

    FAU_PHILFAK_COLORS = {
        "dark": QColor(201, 147, 19),
        "medium": QColor(217, 198, 137),
        "light": QColor(243, 238, 223),
    }
