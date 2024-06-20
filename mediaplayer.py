import os
import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QApplication, QSlider, QPushButton, QFileDialog, \
    QHBoxLayout, QFrame, QLabel, QStyle, QToolTip
from PySide6.QtGui import QAction, QPalette, QColor
from PySide6.QtCore import Qt, QTimer
import vlc


class MediaPlayerWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Media Player")

        # Create a basic vlc instance
        self.instance = vlc.Instance('--vout=opengl')  # For Linux/macOS
        # self.instance = vlc.Instance('--vout=direct3d11')  # For Windows

        self.media = None

        # Create an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.create_ui()
        self.is_paused = False

    def create_ui(self):
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        self.videoframe = QFrame()

        self.palette = self.videoframe.palette()
        self.palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        # Create a slider for video position
        self.positionslider = CustomSlider(Qt.Orientation.Horizontal, self.set_position, self)
        self.positionslider.setMaximum(1000)
        self.positionslider.sliderMoved.connect(self.set_position)

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

        self.speedslider = CustomSlider(Qt.Orientation.Horizontal, self.set_speed, self)
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
        self.volumeslider = CustomSlider(Qt.Orientation.Horizontal, self.set_volume, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeslider.setToolTip("Volume")
        self.hbuttonbox.addWidget(self.volumeslider)
        self.volumeslider.valueChanged.connect(self.set_volume)

        self.vboxlayout = QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addWidget(self.positionslider)
        self.vboxlayout.addLayout(self.hbuttonbox)

        self.widget.setLayout(self.vboxlayout)

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
            self.set_position(self.positionslider.value() -10)
        else:
            self.set_position(self.positionslider.value()+10)

    def open_file(self):
        dialog_txt = "Choose Media File"
        filename, _ = QFileDialog.getOpenFileName(self, dialog_txt, os.path.expanduser('~'))
        if not filename:
            return

        self.media = self.instance.media_new(filename)
        self.mediaplayer.set_media(self.media)

        self.media.parse()

        self.setWindowTitle(self.media.get_meta(vlc.Meta.Title))

        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.mediaplayer.set_xwindow(int(self.videoframe.winId()))
        elif sys.platform == "win32":  # for Windows
            self.mediaplayer.set_hwnd(int(self.videoframe.winId()))

        self.play_pause()

    def set_volume(self, volume):
        self.mediaplayer.audio_set_volume(volume)

    def set_position(self, position):
        pos = position / 1000.0
        self.mediaplayer.set_position(pos)

    def set_speed(self, speed):
        speed = self.findClosest(self.speedList, speed)
        self.speedslider.setValue(speed)
        self.mediaplayer.set_rate(speed / 100.0)
        self.speedlabel.setText("%.2fx" % (speed / 100.0))

    def update_ui(self):
        media_pos = int(self.mediaplayer.get_position() * 1000)
        self.positionslider.setValue(media_pos)

        if not self.mediaplayer.is_playing():
            self.timer.stop()

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


class CustomSlider(QSlider):
    def __init__(self, orientation, pressFunction, parent=None):
        super().__init__(orientation, parent)
        self.pressFunction = pressFunction

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            value = QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), pos.x(), self.width())
            self.setValue(value)
            self.pressFunction(value)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        value = self.minimum() + (self.maximum()-self.minimum()) * pos.x() / self.width()
        QToolTip.showText(event.globalPos(), str(int(value)))
        super().mouseMoveEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MediaPlayerWindow()
    player.show()
    player.resize(640, 480)
    sys.exit(app.exec())
