import time
import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QApplication, QSlider, QPushButton, QFileDialog, \
    QHBoxLayout, QFrame, QLabel, QStyle, QToolTip, QSpacerItem, QSizePolicy
from PySide6.QtGui import QAction, QPalette, QColor, QPixmap, QIcon
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
import vlc


class SliderTypes:
    VOLUME = 0
    POSITION = 1
    SPEED = 2


class MediaPlayerWindow(QMainWindow):
    starting_time = 0

    def __init__(self, pixmap, location, time_interval):
        super().__init__()

        self.first_encounter = time_interval[0]
        self.last_encounter = time_interval[1]
        self.video_length = (time.time_ns() / 1000000) - self.starting_time

        self.setWindowTitle("Media Player")

        # Create a basic vlc instance
        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.instance = vlc.Instance('--vout=opengl')  # For Linux/macOS
        elif sys.platform == "win32":  # for Windows
            self.instance = vlc.Instance('--vout=direct3d11')  # For Windows

        self.media = None

        # Create an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.create_ui(pixmap, location, time_interval)
        self.is_paused = False

        self.open_file()

    def create_ui(self, pixmap, location, time_interval):
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        self.videoframe = QFrame()
        self.videoframe.resize(640, 480)

        self.videoframe.palette().setColor(QPalette.Window, QColor(0, 0, 0))
        self.videoframe.setAutoFillBackground(True)

        # Create a slider for video position
        self.hdurationbox = QHBoxLayout()
        self.duration_label = QLabel("00:00:00")
        self.duration_slider = CustomSlider(Qt.Orientation.Horizontal, self.set_position, SliderTypes.POSITION, self)
        self.duration_slider.setMaximum(1000)
        self.duration_slider.sliderMoved.connect(self.set_position)
        self.hdurationbox.addWidget(self.duration_label)
        self.hdurationbox.addWidget(self.duration_slider)

        # Create a horizontal box layout
        self.hbuttonbox = QHBoxLayout()

        # Create a play button
        self.playbutton = QPushButton("Play")
        self.hbuttonbox.addWidget(self.playbutton)
        self.playbutton.clicked.connect(self.play_pause)

        # Create move forward and backward buttons
        self.backbutton = QPushButton("<")
        self.forwardbutton = QPushButton(">")
        self.hbuttonbox.addWidget(self.backbutton)
        self.hbuttonbox.addWidget(self.forwardbutton)
        self.backbutton.clicked.connect(lambda: self.forward_backward(1))
        self.forwardbutton.clicked.connect(lambda: self.forward_backward(0))

        # Create a speed slider
        self.speedList = (50, 100, 200, 300, 400)

        self.hbuttonbox.addStretch(1)
        self.speedlabel = QLabel("1.00x")
        self.hbuttonbox.addWidget(self.speedlabel)

        self.speedslider = CustomSlider(Qt.Orientation.Horizontal, self.set_speed, SliderTypes.SPEED, self)
        self.speedslider.setMaximum(400)  # Set maximum speed to 4x
        self.speedslider.setValue(100)  # Set default speed to 1x
        self.speedslider.setToolTip("Speed")
        self.speedslider.setTickInterval(100)
        self.speedslider.setTickPosition(QSlider.TicksBelow)
        self.hbuttonbox.addWidget(self.speedslider)
        self.speedslider.valueChanged.connect(self.set_speed)

        # Create a volume slider
        self.hbuttonbox.addStretch(1)
        self.volumelabel = QLabel("Volume: ")
        self.hbuttonbox.addWidget(self.volumelabel)
        self.volumeslider = CustomSlider(Qt.Orientation.Horizontal, self.set_volume, SliderTypes.VOLUME, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeslider.setToolTip("Volume")
        self.hbuttonbox.addWidget(self.volumeslider)
        self.volumeslider.valueChanged.connect(self.set_volume)

        self.vboxlayout = QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addLayout(self.hdurationbox)
        self.vboxlayout.addLayout(self.hbuttonbox)

        # Add Button
        self.open_menu_button = QPushButton(icon=QIcon("uifolder/assets/icons/16x16/cil-caret-right.png"),
                                            styleSheet="background-color: rgb(44, 49, 60);")
        self.open_menu_button.clicked.connect(self.open_close_menu)
        self.open_menu_button.setMaximumSize(25, 25)
        self.hbuttonbox.addWidget(self.open_menu_button)

        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        # Add actions to file menu
        open_action = QAction("Load Video", self)
        close_action = QAction("Close App", self)
        file_menu.addAction(open_action)
        file_menu.addAction(close_action)

        open_action.triggered.connect(self.open_file)
        close_action.triggered.connect(sys.exit)

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_ui)

        self.volumeslider.setValue(50)
        self.mediaplayer.audio_set_volume(50)

        self.create_menu(pixmap, location, time_interval)
        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.vboxlayout)
        self.main_layout.addWidget(self.menu)
        self.widget.setLayout(self.main_layout)
        self.menu.hide()

    def create_menu(self, pixmap, location, time_interval):
        self.menu = QFrame(self)
        self.menu.setMaximumWidth(200)
        self.menu.resize(200, self.height())
        self.menu.setLayout(QVBoxLayout())

        scaled_pixmap = pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
        image_label = QLabel(pixmap=scaled_pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        self.menu.layout().addWidget(image_label)

        location_label = QLabel("Location: \n" + str(location))
        location_label.setAlignment(Qt.AlignTop)
        self.menu.layout().addWidget(location_label)

        time_interval_label = QLabel("Time Interval: \n" + str(time_interval))
        time_interval_label.setAlignment(Qt.AlignTop)
        self.menu.layout().addWidget(time_interval_label)

        button = QPushButton("Show on Map")
        self.menu.layout().addWidget(button)

        self.menu.layout().addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def open_close_menu(self):
        width = self.menu.width()

        # SET MAX WIDTH
        if self.menu.isHidden():
            self.resize(self.width() + width, self.height())
            self.menu.show()
        else:
            self.resize(self.width() - width, self.height())
            self.menu.hide()

    def play_pause(self):
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playbutton.setText("Play")
            self.is_paused = True
            self.timer.stop()
        else:
            if self.mediaplayer.play() == -1:
                self.open_file()
                return
            self.mediaplayer.play()
            self.playbutton.setText("Pause")
            self.timer.start()
            self.is_paused = False

    def forward_backward(self, which):
        if which == 1:
            self.set_position(self.duration_slider.value() - self.ten_seconds)
            self.duration_slider.setValue(self.duration_slider.value() - self.ten_seconds)
        else:
            self.set_position(self.duration_slider.value() + self.ten_seconds)
            self.duration_slider.setValue(self.duration_slider.value() + self.ten_seconds)
        watched_second = self.mediaplayer.get_position() * self.video_length / 1000
        self.duration_label.setText(
            "%02d:%02d:%02d" % (watched_second // 3600, (watched_second // 60) % 60, watched_second % 60))

    def open_file(self, filename="output.avi"):
        # dialog_txt = "Choose Media File"
        # filename, _ = QFileDialog.getOpenFileName(self, dialog_txt, os.path.expanduser('~'))
        # if not filename:
        #     return

        self.media = self.instance.media_new(filename)
        self.mediaplayer.set_media(self.media)

        self.media.parse()

        self.ten_seconds = 10000 / self.video_length

        self.setWindowTitle(self.media.get_meta(vlc.Meta.Title))

        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.mediaplayer.set_xwindow(int(self.videoframe.winId()))
        elif sys.platform == "win32":  # for Windows
            self.mediaplayer.set_hwnd(int(self.videoframe.winId()))

        self.play_pause()

        self.set_position(self.first_encounter / self.video_length * 1000)

    def set_volume(self, volume):
        self.mediaplayer.audio_set_volume(volume)

    def set_position(self, position):
        if position < 0:
            position = 0
        elif position > 1000:
            position = 1000
        pos = position / 1000.0
        self.mediaplayer.set_position(pos)
        watched_second = pos * self.video_length / 1000
        self.duration_label.setText(
            "%02d:%02d:%02d" % (watched_second // 3600, (watched_second // 60) % 60, watched_second % 60))

    def set_speed(self, speed):
        speed = self.findClosest(self.speedList, speed)
        self.speedslider.setValue(speed)
        self.mediaplayer.set_rate(speed / 100.0)
        self.speedlabel.setText("%.2fx" % (speed / 100.0))

    def update_ui(self):
        self.video_length = (time.time_ns() / 1000000) - self.starting_time
        media_pos = int(self.mediaplayer.get_position() * 1000)
        self.duration_slider.setValue(media_pos)
        watched_second = self.mediaplayer.get_position() * self.video_length / 1000
        self.duration_label.setText(
            "%02d:%02d:%02d" % (watched_second // 3600, (watched_second // 60) % 60, watched_second % 60))

        if not self.mediaplayer.is_playing():
            self.timer.stop()
            if not self.is_paused:
                self.is_paused = True
                self.playbutton.setText("Play")
                self.mediaplayer.stop()

        if self.mediaplayer.get_position() < self.last_encounter / self.video_length + 0.01 and self.mediaplayer.get_position() > self.last_encounter / self.video_length - 0.01:
            self.play_pause()

    def findClosest(self, array, value):
        array = sorted(array)
        for x in range(len(array)):
            if value <= array[x]:
                if x == 0:
                    return array[x]
                if array[x] - value < value - array[x - 1]:
                    return array[x]
                else:
                    return array[x - 1]

    def set_starting_time(self, time):
        self.starting_time = time

    def closeEvent(self, event):
        self.mediaplayer.stop()
        event.accept()


class CustomSlider(QSlider):
    def __init__(self, orientation, pressFunction, type, parent=None):
        super().__init__(orientation, parent)
        self.pressFunction = pressFunction
        self.prnt = parent
        self.type = type
        self.firstEncounter = self.prnt.first_encounter
        self.lastEncounter = self.prnt.last_encounter

        if self.type == SliderTypes.POSITION:
            self.first_encounter_label = QLabel(parent=self)
            self.first_encounter_label.resize(10, 15)
            self.first_encounter_label.setStyleSheet("background-color: rgba(0, 0, 0, 155);")

            self.last_encounter_label = QLabel(parent=self)
            self.last_encounter_label.resize(10, 15)
            self.last_encounter_label.setStyleSheet("background-color: rgba(0, 0, 0, 155);")

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            value = QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), pos.x(), self.width())
            self.setValue(value)
            self.pressFunction(value)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = (self.minimum() + (self.maximum() - self.minimum()) * event.pos().x() / self.width())

        if self.type == SliderTypes.POSITION:
            second = pos * self.prnt.video_length / (1000 * 1000)
            time = "%02d:%02d:%02d" % (second // 3600, (second // 60) % 60, second % 60)
            QToolTip.showText(event.globalPos(), time)
        elif self.type == SliderTypes.VOLUME:
            QToolTip.showText(event.globalPos(), str(int(pos)))
        elif self.type == SliderTypes.SPEED:
            QToolTip.showText(event.globalPos(), str(int(pos / 100)))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        pos = (self.minimum() + (self.maximum() - self.minimum()) * event.pos().x() / self.width())
        # If the mouse is on the first encounter label
        if self.type == SliderTypes.POSITION:
            firstpos = (self.minimum() + (self.maximum() - self.minimum()) * self.first_pos / self.width())
            if (pos > firstpos - 40) and (pos < firstpos + 40):
                self.prnt.set_position(firstpos)
                self.prnt.duration_slider.setValue(firstpos)
                watched_second = firstpos * self.prnt.video_length / 1000
                self.prnt.duration_label.setText(
                    "%02d:%02d:%02d" % (watched_second // 3600, (watched_second // 60) % 60, watched_second % 60))
        super().mouseReleaseEvent(event)

    def update_ui(self):
        if self.type == SliderTypes.POSITION:
            value = int(self.prnt.first_encounter / self.prnt.video_length * 1000)
            self.first_pos = QStyle.sliderPositionFromValue(self.minimum(), self.maximum(), value, self.width())
            self.first_encounter_label.move(self.first_pos, 0)
            value = int(self.prnt.last_encounter / self.prnt.video_length * 1000)
            pos = QStyle.sliderPositionFromValue(self.minimum(), self.maximum(), value, self.width())
            self.last_encounter_label.move(pos, 0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    sample_pixmap = QPixmap("Database/data/2.jpg")
    player = MediaPlayerWindow(sample_pixmap, (12.412345718, 15.1728378124),
                               (3000, 10000))
    player.show()
    player.resize(640, 480)
    sys.exit(app.exec())
