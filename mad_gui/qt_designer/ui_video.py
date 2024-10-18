from PySide6.QtCore import QSize, Qt
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy, QSlider, QVBoxLayout, QWidget


class UiVideoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video")
        self.verticalLayout = QVBoxLayout()
        self.view_video = QVideoWidget()
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.view_video.sizePolicy().hasHeightForWidth())
        self.view_video.setSizePolicy(size_policy)
        self.view_video.setMinimumSize(QSize(0, 200))
        self.view_video.setMaximumSize(QSize(1666666, 500))
        self.view_video.setSizeIncrement(QSize(0, 0))
        self.view_video.setBaseSize(QSize(0, 0))
        self.view_video.setFocusPolicy(Qt.NoFocus)
        self.view_video.setAcceptDrops(False)
        self.resize(876 // 2, 705 // 2)
        self.view_video.setAutoFillBackground(True)
        self.view_video.setStyleSheet("")
        self.view_video.setObjectName("view_video")
        self.verticalLayout.addWidget(self.view_video)

        self.player = QMediaPlayer()

        self.horizontalLayout = QHBoxLayout()

        self.btn_play_pause = QPushButton()
        self.btn_play_pause.setMaximumSize(QSize(150, 16777215))
        self.btn_play_pause.setObjectName("btn_play_pause")
        self.btn_play_pause.setText("Play / Pause")
        self.horizontalLayout.addWidget(self.btn_play_pause)

        self.slider = QSlider()
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setObjectName("slider")
        self.slider.setTickInterval(10)
        self.slider.setSingleStep(10)
        self.slider.setStyleSheet("QSlider::handle:horizontal{background-color: rgb(255,255,0);}")
        self.horizontalLayout.addWidget(self.slider)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.setLayout(self.verticalLayout)
        self.slider_is_pressed = False
